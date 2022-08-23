#! /usr/bin/env python

'''Module for managing the picamera

'''

import logging
from picamera import PiCamera

_picam = PiCamera()
_picam.close()

ports = [0,1,2,3]
config = None

def close():
    assert(_picam.recording is False)
    _picam.close()


def get_camera():
    if _picam.closed:
        _picam = PiCamera(camera_num=0, stereo_mode='none',
                           stereo_decimate=False,
                           resolution=resolution,
                           framerate=framerate, sensor_mode=0,
                           led_pin=None, clock_mode='reset',
                           framerate_range=None )
    return _picam

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]
    

class PiCameraManager(metaclass=Singleton):
    pass


if __name__=='__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)

    cam1 = PiCameraManager()
    cam2 = PiCameraManager()

    logging.debug(f"Camera 1: {cam1}")
    logging.debug(f"Camera 2: {cam2}")
    assert(cam1==cam2)
    
