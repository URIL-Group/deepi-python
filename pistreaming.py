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

WebSocketWSGIHandler.http_version = '1.1'

###########################################
# CONFIGURATION
_JSMPEG_MAGIC = b'jsmp'
_JSMPEG_HEADER = Struct('>4sHH')
HTTP_PORT = 8082
WS_PORT = 8084

VFLIP = False
HFLIP = False

COLOR = u'#444'
BGCOLOR = u'#333'

###########################################


class StreamingHttpHandler(BaseHTTPRequestHandler):
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
            tpl = Template(self.server.index_template)
            content = tpl.safe_substitute(dict(
                WS_PORT=WS_PORT, WIDTH=WIDTH, HEIGHT=HEIGHT, COLOR=COLOR,
                BGCOLOR=BGCOLOR))
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
    def __init__(self):
        super(StreamingHttpServer, self).__init__(
                ('', HTTP_PORT), StreamingHttpHandler)
        with io.open('index.html', 'r') as f:
            self.index_template = f.read()
        with io.open('jsmpg.js', 'r') as f:
            self.jsmpg_content = f.read()


class StreamingWebSocket(WebSocket):
    def opened(self):
        self.send(_JSMPEG_HEADER.pack(_JSMPEG_MAGIC, WIDTH, HEIGHT), binary=True)


class BroadcastOutput:
    def __init__(self,resolution,framerate):
        self.converter = Popen([
            '/usr/bin/ffmpeg',
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

    def write(self, b):
        self.converter.stdin.write(b)

    def flush(self):
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


class PiStreamer:
    def __init__(self,resolution,framerate):

        # TODO: allow for resize on call

        self.resolution = resolution
        self.framerate = framerate

        self.websocket_server = make_server(
            '', WS_PORT,
            server_class=WSGIServer,
            handler_class=WebSocketWSGIRequestHandler,
            app=WebSocketWSGIApplication(handler_cls=StreamingWebSocket))
        self.websocket_server.initialize_websockets_manager()
        self.websocket_thread = Thread(
            target=self.websocket_server.serve_forever)
        
        self.output = BroadcastOutput(self.resolution,self.framerate)
        self.broadcast_thread = BroadcastThread(self.output.converter,
                                                self.websocket_server)

        self.websocket_thread.start()
        self.broadcast_thread.start()
            
    def shutdown(self):
        self.broadcast_thread.join()
        self.websocket_server.server_close()
        self.websocket_server.shutdown()
        self.websocket_thread.join()
        self.camera.close()

        


if __name__ == '__main__':
    import picamera
    # print('Initializing HTTP server on port %d' % HTTP_PORT)
    # http_server = StreamingHttpServer()
    # http_thread = Thread(target=http_server.serve_forever)
    # print('Starting HTTP server thread')
    # http_thread.start()
    with picamera.PiCamera() as camera:
        camera.resolution = (WIDTH, HEIGHT)
        camera.framerate = FRAMERATE
        camera.vflip = VFLIP # flips image rightside up, as needed
        camera.hflip = HFLIP # flips image left-right, as needed
        sleep(1) # camera warm-up time

        streamer = PiStreamer(camera.resolution,camera.framerate)
        self.camera.start_recording(streamer.output, 'yuv',resize=streamer.resolution) # NOTE: yuv matches the spawned process
        
        try:
            while camera.recording:
                camera.wait_recording(1)
        except KeyboardInterrupt:
            pass
        finally:
            streamer.join()

    # print('Shutting down HTTP server')
    # http_server.shutdown()
    # print('Waiting for HTTP server thread to finish')
    # http_thread.join()
    print("All finished")

