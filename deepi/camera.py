#! /usr/bin/env python
'''Wrapper for the PiCamera class that automates some portions for the DEEPi

'''

import logging
import os
from time import sleep
from datetime import datetime

from picamera import PiCamera

import camconfig


# TODO: make sure these directories exist
# TODO: put these in the config

def timestamp():
    '''Return a simple timestamp for saving fies

    '''
    return datetime.now().strftime('%Y%m%dT%H%M%S')

# class Singleton(type):
#     '''Singleton metaclass to ensure camera cannot be opened twice

#     '''
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton,
#                                         cls).__call__(*args, **kwargs)
#         else:
#             # cls._instances[cls].__init__(*args, **kwargs)
#             logging.warning("Camera already open! Returning previous instance")
#         return cls._instances[cls]

# class SingletonPiCamera(PiCamera,metaclass=Singleton):
#     '''Redefines picamera as class as a singleton

#     '''

#     def __init__(self):
#         PiCamera.__init__(self)
#         logging.debug(f"Camera initiated:{self}")


def load_camera(config=None) -> PiCamera: 

    picam = PiCamera()

    if config is None:
        config = camconfig.load()

    picam.resolution = config.get('CAMERA','resolution')
    picam.framerate = config.getfloat('CAMERA','framerate')
    picam.hflip = config.getboolean('VIEW','hflip')
    picam.vflip = config.getboolean('VIEW','vflip')
    picam.rotation = config.getint('VIEW','rotation')

    # TODO: led/flash
    # TODO: effects options

    return picam


# class BaseCamera:

#     def __init__(self, picam:PiCamera=None, config=None):

#         if picam is None:
#             self.picam = load_camera(config)

#         if config is None:
#             config = camconfig.load()


class VideoRecorder:
    '''Recorder for video

    '''

    fmt = 'h264'
    recording = False

    def __init__(self, picam:PiCamera, splitter_port:int=1,
                 outpath:str=os.curdir):

        self.picam = picam
        self.port = splitter_port
        self.path = outpath

    @property
    def output(self):
        os.path.join(self.path,timestamp()+'.'+self.fmt)

    def start(self):
        self.picam.start_recording(self.output, splitter_port=self.port)
        self.recording = True
        logging.debug(f"Recording to {self.output}")

    def split(self):
        self.picam.split_recording(self.output, splitter_port=self.port)
        self.recording = True

    def toggle(self):
        if self.recording:
            self.stop()
        else:
            self.start()            

    def stop(self):
        self.picam.split_recording(splitter_port=self.port)
        self.recording = True
        logging.debug("Stopping recording")

        

class StillCamera:
    ''' Simple camera for taking photos

    '''

    fmt = 'jpeg'

    def __init__(self, picam:PiCamera, splitter_port:int=1,
                 outpath:str=os.curdir):
        self.picam = picam
        self.port = splitter_port
        self.path = outpath

    @property
    def output(self):
        os.path.join(self.path,timestamp()+'.'+self.fmt)

    def capture(self):
        logging.debug(f"Capturing to {self.output}")
        self.picam.capture(self.output, use_video_port=True,
                           splitter_port=self.port)



class TimelapseRecorder(StillCamera):

    def start(self):
        pass

    def stop(self):
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
