#! /usr/bin/env python

'''Module for managing the picamera

'''

from picamera import PiCamera

_picam = PiCamera()
_picam.close()

ports = [0,1,2,3]
config = None


def set_config(config_file):
    assert(_picam.closed is True)
    pass


def save_config(config_file):
    pass
    

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
