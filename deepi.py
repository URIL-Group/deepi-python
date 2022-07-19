'''Control module for DEEPi

Russ Shomberg, URI, 2022
'''

import datetime
from time import sleep
try:
    from picamera import PiCamera
except ImportError:
    picamera = None

import yaml
from yaml.loader import SafeLoader

_picam = None

def init():
    _picam = PiCamera( resolution=(1920,1080),
                       framerate=30 )
    sleep(2)


def timestamp(self):
    return datetime.now().strftime('%Y%m%d-%H%M%S.%f')

class Recorder(Thread):

    def __init__(self,picam=None):
        self._picam=picam

    def run(self):
        output
        
        
        

class DeepiCamera:

    def __init__(self):
        self.picam = PiCamera( resolution=(1920,1080),
                               framerate=30
        )
        sleep(2)                # wait for camera to wake up


    def capture(self):
        self.picam.capture(f'~/Pictures/{timestamp()}.png',
                           use_video_port=True,
                           splitter_port=0
        )

    def start_recording(self):
        pass

    def stop_recording(self):
        pass

    def start_stream(self,ouput):
        pass

    def stop_stream(self):
        pass

    def close(self):
        self.stop_recording()
        self.stop_stream()
        self.picam.close()


class Lights:

    def __init__(self):
        self.pin_num = 18

    def turn_on(self):
        pass

    def turn_off(self):
        pass


# TODO: I2C module

# TODO: SPI module

# TODO: ethernet module
# TODO: camera arrays
