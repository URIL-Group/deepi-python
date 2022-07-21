#!/usr/bin/env python

import sys
import io
import os
import shutil
from subprocess import Popen, PIPE
from string import Template
from struct import Struct
from threading import Thread
from time import sleep, time
from http.server import HTTPServer, BaseHTTPRequestHandler
from wsgiref.simple_server import make_server

from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import (
    WSGIServer,
    WebSocketWSGIHandler,
    WebSocketWSGIRequestHandler,
)
from ws4py.server.wsgiutils import WebSocketWSGIApplication


class StreamingHttpHandler(BaseHTTPRequestHandler):
    '''Create a simple webserver to display'''    
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
    def __init__(self,resolution,port=8082, ws_port=8084,):
        HTTPServer.__init__(self, ('', port),
                            StreamingHttpHandler)        
        with io.open('index.html', 'r') as f:
            # self.index_template = f.read()
            tpl = Template(f.read())
            self.index_content = tpl.safe_substitute(dict(
                WS_PORT=ws_port))
        with io.open('jsmpg.js', 'r') as f:
            self.jsmpg_content = f.read()


def make_websocket_server(resolution,port):

    class StreamingWebSocket(WebSocket):

        def opened(self):
            
            JSMPEG_MAGIC = b'jsmp'
            JSMPEG_HEADER = Struct('>4sHH')

            self.send(JSMPEG_HEADER.pack(JSMPEG_MAGIC, resolution[0], resolution[1]), binary=True)
            
    websocket_server = make_server( '', port,
                                    server_class=WSGIServer,
                                    handler_class=WebSocketWSGIRequestHandler,
                                    app=WebSocketWSGIApplication(
                                        handler_cls=StreamingWebSocket ))
    websocket_server.initialize_websockets_manager()
    return websocket_server

class BroadcastOutput(object):
    def __init__(self, resolution,framerate):
        print('Spawning background conversion process')
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
        self.converter.wait()


class BroadcastThread(Thread):
    def __init__(self, converter, websocket_server):
        super(BroadcastThread, self).__init__()
        self.converter = converter
        self.websocket_server = websocket_server

    def run(self):
        try:
            while True:
                buf = self.converter.stdout.read1(32768)
                if buf:
                    self.websocket_server.manager.broadcast(buf, binary=True)
                elif self.converter.poll() is not None:
                    break
        finally:
            self.converter.stdout.close()


class WebSocketStream:
    # TODO: move everthing except the camera here and provide a public
    # `output` for the camaera to record to.

    def __init__(self, resolution, framerate, ws_port):

        print(f'Initializing websockets server on port {ws_port}')
        WebSocketWSGIHandler.http_version = '1.1'
        self.websocket_server = make_websocket_server(resolution, ws_port)
        self.websocket_thread = Thread(target=self.websocket_server.serve_forever)

        print('Initializing broadcast thread')
        self.output = BroadcastOutput(resolution,framerate)
        self.broadcast_thread = BroadcastThread(self.output.converter,
                                                self.websocket_server)
        self.websocket_thread.start()
        self.broadcast_thread.start()

    # TODO: create a start
    # TODO: create shutdown

        



if __name__ == '__main__':

    import picamera

    HTTP_PORT = 8080
    WS_PORT = 8088
    
    print('Initializing camera')
    with picamera.PiCamera() as camera:
        camera.resolution = (1280,720)
        camera.framerate = 30
        camera.vflip = True
        camera.hflip = False 
        sleep(1) # camera warm-up time
        streaming_resolution = (640,480)
        streaming_resolution = (1280,720)

        socket_streamer = WebSocketStream(streaming_resolution,
                                          camera.framerate, WS_PORT)
        
        print(f'Initializing HTTP server on port {HTTP_PORT}')
        http_server = StreamingHttpServer((640,480),
                                          HTTP_PORT, ws_port=WS_PORT)
        http_thread = Thread(target=http_server.serve_forever)

        print('Starting recording')
        camera.start_recording(socket_streamer.output, 'yuv', splitter_port=2,
                               resize=streaming_resolution)

        try:
            print('Starting websockets thread')
            print('Starting HTTP server thread')
            http_thread.start()
            print('Starting broadcast thread')
            while True:
                camera.wait_recording(1,splitter_port=2)
        except KeyboardInterrupt:
            pass
        finally:
            print('Stopping recording')
            camera.stop_recording(splitter_port=2)
            
            print('Waiting for broadcast thread to finish')
            broadcast_thread.join()
            print('Shutting down HTTP server')
            http_server.shutdown()
            print('Shutting down websockets server')
            websocket_server.shutdown()
            print('Waiting for HTTP server thread to finish')
            http_thread.join()
            print('Waiting for websockets thread to finish')
            websocket_thread.join()




