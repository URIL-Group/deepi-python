#!/usr/bin/env python
""" Module for streaming

Based largely on https://github.com/waveform80/pistreaming

"""

import sys
import io
import os
import logging

from subprocess import Popen, PIPE
from struct import Struct
from threading import Thread
from time import sleep, time
from picamera import PiCamera

from wsgiref.simple_server import make_server

from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import ( WSGIServer,
                                         WebSocketWSGIHandler,
                                         WebSocketWSGIRequestHandler,
                                        )
from ws4py.server.wsgiutils import WebSocketWSGIApplication
WebSocketWSGIHandler.http_version = '1.1'


class StreamingWebSocketHandler(WebSocket):
    '''Websocket with a header line added on opening. This websocket handler relies on the the jsmpeg javascript package to act as client. Before using an instance of this class, the resolution must be set based on the streaming resolution of the picamera.
    
    Other than the initial opening behavior, the websocket operates the same as a normal websock.'''
    
    resolution: tuple[int,int] = None

    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        self.resolution: tuple[int,int] = StreamingWebSocketHandler.resolution
        assert self.resolution is not None, "Must set resolution class attribute before initializing."
        # FIXME: currently, the resolution cannot be defined in the constructor because the class itself is passed rather than an instance of the class. Instances are spawned later as connections are established. Multiple connections may be established at the same time.
        WebSocket.__init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None)

    def opened(self):
        '''Runs when a new connection is established. The websocket first sends information to the client about about the stream which is read by a client using jsmpeg.'''
        logging.debug("Websocket connection opened")
        JSMPEG_MAGIC = b'jsmp'
        JSMPEG_HEADER = Struct('>4sHH')
        self.send(JSMPEG_HEADER.pack(JSMPEG_MAGIC, self.resolution[0],
                                    self.resolution[1]), binary=True)            

    def closed(self, code, reason=None):
        # TODO: figure out when and why this runs
        logging.debug("Websocket closed")


class BroadcastOutput:
    '''File-like object that converts video when recorded to. The object is a wrapper for a the spawned `ffmpeg` converter process. The converter is spawned in the background and uses a pipe for the input and output. The converter converts input from raw yuv video to mpeg video'''

    def __init__(self, resolution:tuple[int,int], framerate:int):

        if resolution==(1920,1080):
            logging.warning("Modifying streaming resolution to (1920x1088)")
            # NOTE: this happens automatically, so it must match
            # FIXME: I do not know why it occurs
            resolution = (1920,1088)
        self.resolution = resolution
            
        logging.debug('Spawning background conversion process')
        self.converter = Popen([
            # TODO: understand these options
            'ffmpeg',
            '-f', 'rawvideo',
            '-pix_fmt', 'yuv420p',
            '-s', '%dx%d' % resolution,
            '-r', str(float(framerate)),
            '-i', '-',
            '-f', 'mpeg1video',
            '-b', '800k',
            '-r', str(float(framerate)),
            '-'],
            stdin=PIPE, stdout=PIPE, stderr=io.open(os.devnull, 'wb'),
            shell=False, close_fds=True)

    def write(self, buff):
        '''Writes the contents of `buff` to the converter. Based on being a filelike object.'''
        # TODO: write debug code to figure out when and how often this is called
        self.converter.stdin.write(buff)

    def flush(self):
        '''Based on being a filelike object'''
        logging.debug('Waiting for background conversion process to exit')
        self.converter.stdin.close()
        self.converter.wait()   # FIXME: this point never exits


class BroadcastThread(Thread):
    '''Thread piping broadcast output to websocket server. The thread reads the output from a spawned converter and writes the results to the the websockete server broadcast.'''

    # FIXME: this should probably be the __main__ function of this module and defined elsewhere as a thread

    def __init__(self, converter:Popen, server:WSGIServer):
        Thread.__init__(self)
        self.converter = converter
        self.server = server
        self.running = True
        # self.start()
        # NOTE: uncomment above to start on construction

    def run(self):
        try:
            while self.running:
                buf = self.converter.stdout.read1(32768) 
                # FIXME: where does 32768 come from
                if buf:
                    self.server.manager.broadcast(buf, binary=True)
                elif self.converter.poll() is not None:
                    # FIXME: not sure what poll does in this instance
                    break
        finally:
            logging.debug("Broadcast thread broken")
            self.converter.stdout.close()

    def stop(self):
        logging.debug("Broadcast thread stop requested")
        self.running = False
        self.join()



# TODO: I want WebSocketStream and SocketStream to both inherit from the same class. The main difference being that they 'have' a different type of `output`. The Streamer class they inherit from should act as an interface for the DEEPiController class which will 'have' a DEEPiConfig and other necessary classes depending on that configuration. Individual modules will perform tests without using the config or controller classes

class WebSocketStream:
    '''
    Handles everything needed to stream to a websocket as a composite class.
    '''

    # FIXME: this class is likely excessively complicated. I just took eeverything from the main function and added to this class. 

    def __init__(self,picam:PiCamera, ws_port:int, 
                 resolution:tuple[int,int]=None, splitter_port:int=2):

        # FIXME: picam should probably be a private attribute since it should not be manipulated directly
        self.picam = picam
        self._splitter_port = splitter_port
        self.ws_port = ws_port

        if resolution is None:
            resolution = picam.resolution
        self._resolution:tuple[int,int] = resolution
        # FIXME: check for valid resolutions before settings

        logging.debug(f"Streaming resolution: {resolution}")
        logging.debug(f"Streaming splitter_port: {splitter_port}")
        logging.debug(f"Streaming websocket port: {self.ws_port}")

        StreamingWebSocketHandler.resolution = self.resolution
        self.handler = StreamingWebSocketHandler
        # NOTE: no actual need for this to be defined as an attribute. But doing so makes them show up attached in the UML diagram. Otherwise the handler is left floating

        logging.debug("Opening websocket")
        self.output:BroadcastOutput = BroadcastOutput(self._resolution,
                                      self.picam.framerate)
        
        app = WebSocketWSGIApplication( handler_cls=self.handler )
        self.server = make_server('', port, server_class=WSGIServer,
                            handler_class=WebSocketWSGIRequestHandler,
                            app=app)
        self.server.initialize_websockets_manager()
        self._ws_thread = Thread(target=self.server.serve_forever)
        self.thread = BroadcastThread(self.output.converter, self.server)

        self._ws_thread.start()
        self.thread.start()        
        logging.debug("Starting websocket stream")
        self.picam.start_recording(self.output, 'yuv',
                                   resize=self.resolution,
                                   splitter_port=self._splitter_port)
        self._streaming = True

    @property
    def resolution(self) -> tuple[int,int]:
        return self._resolution

    def shutdown(self):
        # TODO: when is this actually called
        logging.debug("websocketstream shutdown called")
        self.stop()

    def stop(self):
        # TODO: when is this actually called
        logging.debug("Stopping websocketstream")
        self.picam.stop_recording(splitter_port=self._splitter_port)
        self._streaming = False

        self.server.shutdown()
        self._ws_thread.join()
        self.thread.stop()

    def toggle(self):
        # FIXME: do not think this actually works
        if self._streaming:
            self.stop()
        else:
            # FIXME: do not think this actually works
            self.start()
