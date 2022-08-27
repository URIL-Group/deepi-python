import picamera

class PiCamera(picamera.PiCamera):
    def __call__(self):
        return self
    def close(self):
        pass
PiCamera = PiCamera()

if __name__=='__main__':

    cam1 = PiCamera()
    cam2 = PiCamera()
