#! /usr/bin/env python

'''Wrapper for the PiCamera class that automates some portions for the DEEPi

Russ Shomberg, URI, 2022

'''

import logging
from time import sleep
from picamera import PiCamera

import camconfig

IMAGE_DIR = '/home/pi/Pictures/'
VIDEO_DIR = '/home/pi/Videos/'
# TODO: make sure these directories exist

def timestamp():
    return datetime.now().strftime('%Y%m%d-%H%M%S.%f')

class Singleton(type):
    '''Singleton metaclass to ensure camera cannot be opened twice

    '''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        # else:
        #     cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]



class DEEPiCamera(PiCamera,metaclass=Singleton):

    def __init__(self,config=None):
        logging.debug("Starting camera")
        PiCamera.__init__(self)
        sleep(2) # camera warm-up time
        if config is None:
            config=camconfig.get_default()
        self.config = config

    @property
    def config(self):
        pass                    # TODO

    @config.setter
    def config(self, config):
        self.resolution = config['resolution']
        self.framerate = config['framerate']
        self.rotation = config['rotation']
        self.vflip = config['vflip']
        self.hflip = config['hflip']
        self.iso = config['iso']
        self.shutter = config['shutter_speed']
        self.brightness = config['brightness']
        self.contrast = config['contrast']
        self.saturation = config['saturation']
        self.sharpness = config['sharpness']
        self.led = config['led']
        self.flash = config['flash_mode']
    
        
if __name__=='__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)

    cam1 = DEEPiCamera()
    cam2 = DEEPiCamera()

    logging.debug(f"Camera 1: {cam1}")
    logging.debug(f"Camera 2: {cam2}")
    assert(cam1==cam2)
