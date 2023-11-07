import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from string import Template
import io
from threading import Thread
from time import time


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
        with io.open('deepi/index.html', 'r') as f:
            tpl = Template(f.read())
            self.index_content = tpl.safe_substitute(dict(
                WS_PORT=ws_port))
        with io.open('deepi/jsmpg.js', 'r') as f:
            self.jsmpg_content = f.read()

            
if __name__ == '__main__':

    logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)

    from deepi import WebSocketStream
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

        streamer.start()
        logging.info('Starting recording')
        # camera.start_recording(streamer.output, 'yuv', splitter_port=2,
        #                        resize=streaming_resolution)
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

