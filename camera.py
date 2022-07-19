import numpy
import io
import socket
import struct
from threading import Condition

class SplitFrames:
    def __init__(self,connection):
        self.connection = connection
        self.stream = io.BytesIO

    def write(self.buf):
        if buf.startswith(b'\xff\xd8'):
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
            self.stream.write(buf)

            
    
class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Co

class BaseCamera:
    pass


class CvCamera(BaseCamera):

    def __init__(self):
        self._cam = cv2.VideoCapture(0)


    def capture(self):
        ret,image = self._cam.read()
        return image

    def stream(self):
        ret = True
        frame = []
        while ret:
            ret,frame = self._cam.read()
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break            

if __name__=="__main__":

    cam = CvCamera()
    cam.stream()
