import io
import socket
import struct
import time
from picamera import PiCamera
import logging
import typing

class SocketOutput(typing.IO):
    ''' Filelike object for recording mjpeg and writing to socket
    '''
    def __init__(self, connection:socket.SocketIO):
        self.connection = connection
        self.stream:io.BytesIO = io.BytesIO()

    def write(self, buf) -> None:
        '''Write to contents of `buf` to the the stream. If buf represents a new frame, the current contents of the stream are first written to the socket connection and then flushed along with a header.'''
        # TODO: test how often write is called and how oten it represents a new frame
        if buf.startswith(b'\xff\xd8'): # is this a new frame
            # TODO: investigate jpeg frame formats
            # Start of new frame; send the old one's length
            # then the data
            size = self.stream.tell()
            if size > 0: # skip for empty frame (occurs at inital)
                # Send frame header including size.
                self.connection.write(struct.pack('<L', size))
                self.connection.flush() # ???: what does flush do here
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.stream.seek(0)
        self.stream.write(buf)

    def flush(self):
        '''Not sure if this is necessary or if it does anything'''
        logging.debug("SocketOutput.flush called")
        # TODO: impliment

class SocketStreamer:
    

    def __init__(self, picam:PiCamera=None, port:int=8000):

        if picam is None:
            picam = PiCamera()

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0',port))
        self.sock.listen(0)

        logging.info(f"Ready to connect streamer on port {port}")
        self.connection:socket.SocketIO = self.sock.accept()[0].makefile('wb')
        logging.info("Streamer connected")
        self.output:SocketOutput = SocketOutput(self.connection)
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
            self.connection.write(struct.pack('<L', 0))
        except Exception as e:
            logging.debug(f"Error on stop_recording {e}")

    def close(self):
        try:
            self.connection.close()
        except BrokenPipeError as e:
            logging.debug("Connection already closed")
        self.sock.close()


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

    logging.debug("Started socket streaming thread")
    while True:
        with  SocketStreamer(8000) as output:
                
            picam.start_recording(output, format='mjpeg', 
                                 splitter_port=splitter_port)
            start = time.time()
            try:
                while True:
                    picam.wait_recording(5, splitter_port=splitter_port)
            except Exception as e:
                logging.debug(f"Error on wait_recording: {e}")

            finish = time.time()
            try:
                picam.stop_recording(splitter_port=splitter_port)
            except BrokenPipeError:
                pass
            except Exception as e:
                logging.debug(f"Error on stop_recording: {e}")
                                

        logging.debug("Lost connection or closed")
        logging.info(f'Sent {output._count} frames in {finish-start:.1f} seconds '\
                    f'({output._count/(finish-start):.1f}fps)')
        time.sleep(1)        
    logging.debug("Restarting socket streamer")

