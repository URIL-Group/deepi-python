import io
import socket
import struct
import time
import picamera

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

    def __init__(self,picam:picamera.PiCamera,port=8000):

        self.picam = picam

        self.s = socket.socket()
        self.s.bind(('0.0.0.0',port))
        self.s.listen(0)
        print("Ready to connect")
        # Accept a single connection and make a file-like object out of it
        self.conn = self.s.accept()[0].makefile('wb')
        self.output = SplitFrames(self.conn)

    def start(self):
        self.picam.start_recording(self.output, format='mjpeg')

    def stop(self):
        self.picam.stop_recording()

    def close(self):
        self.conn.write(struct.pack('<L', 0))
        self.conn.close()
        self.s.close()



if __name__=='__main__':

    picam = picamera.PiCamera(resolution='HD', framerate=30)
    time.sleep(2)

    feed = SocketStreamer(picam,8000)
    start = time.time()
    feed.start()
    picam.wait_recording(10)
    feed.stop()
    
    finish = time.time()
    print(f'Sent {feed.output.count} images in {finish-start:.1f} seconds')
    print(f'{feed.output.count/(finish-start):.1f}ffps')
