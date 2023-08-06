import io
import socket
import struct
import time
from picamera import PiCamera
import logging

class SplitFrames:
    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; send the old one's length
            # then the data
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)

class SocketStreamer:

    def __init__(self, port=8000):

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0',port))
        self.sock.listen(0)

        logging.info(f"Ready to connect streamer on port {port}")
        self.conn = self.sock.accept()[0].makefile('wb')
        logging.info("Streamer connected")

        self.output = SplitFrames(self.conn)
        logging.debug("Output started")

    def __enter__(self):
        logging.debug(f"Entering streaming context on port")
        return self.output

    def __exit__(self,exc_type,exc_value,exc_tb):
        logging.debug("Exiting streaming context")
        self.stop()
        self.close()

    def stop(self):
        try:
            self.conn.write(struct.pack('<L', 0))
        except Exception as e:
            logging.debug(f"Error on stop_recording {e}")

    def close(self):
        try:
            self.conn.close()
        except BrokenPipeError as e:
            logging.debug("Connection already closed")
        self.sock.close()


from threading import Thread
class SocketStreamingThread(Thread):

    def __init__(self, picam:PiCamera, port=8000, splitter_port=2):
        self.port = port
        self.picam = picam
        self.splitter_port = splitter_port
        Thread.__init__(self)
        Thread.start(self)

    def run(self):
        logging.debug("Started socket streaming thread")
        while True:
            with  SocketStreamer(8000) as output:
                    
                self.picam.start_recording(output, format='mjpeg', 
                                           splitter_port=self.splitter_port)
                start = time.time()
                try:
                    while True:
                        self.picam.wait_recording(video_split_period, splitter_port=self.splitter_port)
                except Exception as e:
                    pass

                finish = time.time()
                try:
                    self.picam.stop_recording(splitter_port=self.splitter_port)
                except BrokenPipeError:
                    pass

            logging.debug("Lost connection or closed")
            logging.info(f'Sent {output.count} frames in {finish-start:.1f} seconds '\
                        f'({output.count/(finish-start):.1f}fps)')
            time.sleep(1)        
        logging.debug("Restarting socket streamer")



if __name__=='__main__':

    resolution = '1080p'
    framerate = 24
    video_split_period = 10*60
    port = 8000
    splitter_port = 2

    # resolution = (1920,1080)
    # framerate = 60
    logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)

    picam  = PiCamera(resolution=resolution, framerate=framerate)
    time.sleep(2) # warm up camera

    logging.info(f"Starting socket streaming thread on port {port}")
    socket_streaming_thread = SocketStreamingThread(picam, port, splitter_port = 2)
    
    logging.debug("Node script ended")
