#! /usr/bin/env python
'''Wrapper for the PiCamera class that automates some portions for the DEEPi

'''

import logging
from time import sleep
from picamera import PiCamera
import camconfig

# TODO: make sure these directories exist
# TODO: put these in the config

def timestamp():
    '''Return a simple timestamp for saving fies

    '''
    return datetime.now().strftime('%Y%m%d-%H%M%S.%f')

class Singleton(type):
    '''Singleton metaclass to ensure camera cannot be opened twice

    '''
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton,
                                        cls).__call__(*args, **kwargs)
        # else:
        #     cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]

class SingletonPiCamera(PiCamera,metaclass=Singleton):
    '''Redefines picamera as class as a singleton

    '''

    def __init__(self):
        PiCamera.__init__(self)
        logging.debug(f"Camera initiated:{self}")

class BaseCamera:

    def __init__(self,config=None):
        self._picam = SingletonPiCamera()
        if config is None:
            config = camconfig.load()
        self._config = config

        self.resolution = config.get('CAMERA','resolution')
        self.framerate = config.getfloat('CAMERA','framerate')
        # TODO: led/flash
        # TODO: effects options
        self.hflip = config.getboolean('VIEW','hflip')
        self.vflip = config.getboolean('VIEW','vflip')
        self.rotation = config.getint('VIEW','rotation')

    @property
    def resolution(self):
        return self._picam.resolution

    @resolution.setter
    def resolution(self, val):
        if not self._picam.recording:
            self._picam.resolution = val

    @property
    def framerate(self):
        return self._picam.framerate

    @framerate.setter
    def framerate(self, val):
        if not self._picam.recording:
            self._picam.framerate = val

    @property
    def hflip(self):
        return self._picam.hflip

    @hflip.setter
    def hflip(self, val):
        self._picam.hflip = val

    @property
    def vflip(self):
        return self._picam.vflip

    @vflip.setter
    def vflip(self, val):
        self._picam.vflip = val

    @property
    def rotation(self):
        return self._picam.rotation

    @rotation.setter
    def rotation(self, val):
        self._picam.rotation = val
        
            

class VideoRecorder(BaseCamera):

    def start(self):
        pass

    def stop(self):
        pass


class StillCamera(BaseCamera):

    def capture(self):
        pass


class TimelapseRecorder(StillCamera):

    def start(self):
        pass

    def stop(self):
        pass    
    

class VideoStreamer(VideoRecorder):
    # TODO: move to web stream
    pass

if __name__=='__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)

    cam1 = BaseCamera()
    cam2 = VideoRecorder()
    cam3 = StillCamera()

    logging.debug(f"Camera 1: {cam1._picam}")
    logging.debug(f"Camera 2: {cam2._picam}")
    logging.debug(f"Camera 3: {cam3._picam}")
