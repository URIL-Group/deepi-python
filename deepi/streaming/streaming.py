#!/usr/bin/env python
""" Module for streaming

Based largely on https://github.com/waveform80/pistreaming

"""

import sys
import io
import os
import shutil
import logging

from subprocess import Popen, PIPE
from string import Template
from struct import Struct
from threading import Thread
from time import sleep, time

from http.server import HTTPServer, BaseHTTPRequestHandler
from wsgiref.simple_server import make_server

from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import ( WSGIServer,
                                         WebSocketWSGIHandler,
                                         WebSocketWSGIRequestHandler,
                                        )
from ws4py.server.wsgiutils import WebSocketWSGIApplication

WebSocketWSGIHandler.http_version = '1.1'

def make_websocket_server(output,port):
    '''Factory function for websocket server'''

    class StreamingWebSocket(WebSocket):
        '''Websocket with a header line added on opening'''

        def opened(self):
            JSMPEG_MAGIC = b'jsmp'
            JSMPEG_HEADER = Struct('>4sHH')
            self.send(JSMPEG_HEADER.pack(JSMPEG_MAGIC, output.resolution[0],
                                         output.resolution[1]), binary=True)
            

        def closed(self, code, reason=None):
            pass


    app = WebSocketWSGIApplication( handler_cls=StreamingWebSocket )
    server = make_server('', port, server_class=WSGIServer,
                         handler_class=WebSocketWSGIRequestHandler,
                         app=app)
    server.initialize_websockets_manager()
    return server

class BroadcastOutput:
    '''File-like object that converts video when recorded to'''

    def __init__(self, resolution, framerate):

        self.resolution = resolution
            
        logging.info('Spawning background conversion process')
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
            '-r', str(float(framerate)), # ???: double framerate
            '-'],
            stdin=PIPE, stdout=PIPE, stderr=io.open(os.devnull, 'wb'),
            shell=False, close_fds=True)

    def write(self, b):
        self.converter.stdin.write(b)

    def flush(self):
        print('Waiting for background conversion process to exit')
        self.converter.stdin.close()
        self.converter.wait()   # FIXME: this point never exits



class BroadcastThread(Thread):
    '''Thread piping broadcast output to websocket'''

    def __init__(self, converter, server):
        Thread.__init__(self)
        self.converter = converter
        self.server = server
        self.running = True

    def run(self):
        try:
            while self.running:
                buf = self.converter.stdout.read1(32768)
                if buf:
                    self.server.manager.broadcast(buf, binary=True)
                elif self.converter.poll() is not None:
                    break
        finally:
            self.converter.stdout.close()

    def stop(self):
        self.running = False
        self.join()


class WebSocketStream:

    streaming = False

    def __init__(self,picam, ws_port, resolution=None, splitter_port=2):

        self.picam = picam
        self.splitter_port = splitter_port
        self.port = ws_port

        if resolution is None:
            resolution = picam.resolution
        self._resolution = resolution

        logging.debug(f"Streaming resolution: {resolution}")
        logging.debug(f"Streaming splitter_port: {splitter_port}")
        logging.debug(f"Streaming websocket port: {self.port}")

        self.output = None
        self.ws_server = None
        self.ws_thread = None
        self.broadcast_thread = None

    @property
    def resolution(self):
        return self._resolution

    def shutdown(self):
        self.stop()

    def start(self):
        logging.debug("Opening websocket")
        self.output = BroadcastOutput(self._resolution,
                                      self.picam.framerate)
        self.ws_server = make_websocket_server(self.output, self.port)
        self.ws_thread = Thread(target=self.ws_server.serve_forever)
        self.broadcast_thread = BroadcastThread(self.output.converter,
                                                self.ws_server)

        self.ws_thread.start()
        self.broadcast_thread.start()

        logging.debug("Starting websocket stream")
        self.picam.start_recording(self.output, 'yuv',
                                   resize=self._resolution,
                                   splitter_port=self.splitter_port)
        self.streaming = True

    def stop(self):
        logging.debug("Stopping websocket stream")
        self.picam.stop_recording(splitter_port=self.splitter_port)
        self.streaming = False

        logging.debug("Shutting down stream")
        self.ws_server.shutdown()
        self.ws_thread.join()
        self.broadcast_thread.stop()

    def toggle(self):
        if self.streaming:
            self.stop()
        else:
            self.start()


class StreamingHttpHandler(BaseHTTPRequestHandler):
    '''Create a simple webserver to display'''    
    # FIXME: this class only exists for testing purposes.
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
            return
        elif self.path == '/jsmpg.js':
            content_type = 'application/javascript'
            content = self.server.jsmpg_content
        elif self.path == '/index.html':
            content_type = 'text/html; charset=utf-8'
            content = self.server.index_content
        else:
            self.send_error(404, 'File not found')
            return
        content = content.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', len(content))
        self.send_header('Last-Modified', self.date_time_string(time()))
        self.end_headers()
        if self.command == 'GET':
            self.wfile.write(content)


class StreamingHttpServer(HTTPServer):
    # FIXME: this class only exists for testing purposes.
    def __init__(self,port=8082, ws_port=8084):
        addr = ('',port)
        HTTPServer.__init__(self, addr, StreamingHttpHandler)        
        with io.open('index.html', 'r') as f:
            tpl = Template(f.read())
            self.index_content = tpl.safe_substitute(dict(
                WS_PORT=ws_port))
        with io.open('jsmpg.js', 'r') as f:
            self.jsmpg_content = f.read()


if __name__ == '__main__':

    logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)
    
    from picamera import PiCamera as DEEPiCamera

    HTTP_PORT = 8080
    WS_PORT = 8082

    streaming_resolution = (640,480)
    
    logging.info('Initializing camera')
    with DEEPiCamera() as camera:
        
        logging.info(f'Initializing HTTP server on port {HTTP_PORT}')
        http_server = StreamingHttpServer(HTTP_PORT, ws_port=WS_PORT)
        http_thread = Thread(target=http_server.serve_forever)
        http_thread.start()

        logging.info('Starting websockets thread')
        streamer = WebSocketStream(camera,WS_PORT,
                                   resolution=streaming_resolution,
                                   splitter_port=2)

        logging.info('Starting recording')
        camera.start_recording(streamer.output, 'yuv', splitter_port=2,
                               resize=streaming_resolution)
        try:

            while True:
                camera.wait_recording(1,splitter_port=2)
        except KeyboardInterrupt:
            pass
        finally:
            logging.info('Stopping recording')
            camera.stop_recording(splitter_port=2)
            streamer.shutdown()

            logging.info('Shutting down HTTP server')
            http_server.shutdown()
            logging.info('Waiting for HTTP server thread to finish')
            http_thread.join()
