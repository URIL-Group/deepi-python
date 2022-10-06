#! /usr/bin/env python
'''Wrapper for the PiCamera class that automates portions for DEEPi

'''

import logging
import os
from pathlib import Path
from time import sleep
from datetime import datetime
from threading import Thread, Event

from picamera import PiCamera

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
        return os.path.join(self.path,timestamp()+'.'+self.fmt)

    def start(self):
        self.picam.start_recording(self.output, splitter_port=self.port)
        self.recording = True
        logging.debug(f"Recording to {self.output}")

    def split(self):
        logging.debug(f"Splitting recording to {self.output}")
        self.picam.split_recording(self.output, splitter_port=self.port)
        self.recording = True

    def toggle(self):
        if self.recording:
            self.stop()
        else:
            self.start()            

    def stop(self):
        self.picam.stop_recording(splitter_port=self.port)
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
        self.timelapse = None

    @property
    def output(self):
        return os.path.join(self.path,timestamp()+'.'+self.fmt)

    def capture(self):
        logging.info(f"Capturing to {self.output}")
        self.picam.capture(self.output, use_video_port=True,
                           splitter_port=self.port)

    def start_timelapse(self,interval:int=600):
        self.timelapse = TimelapseThread(self.picam, interval)
        self.timelapse.start()

    def stop_timelapse(self):
        self.timelapse.stop()
        self.timelapse.join()


class TimelapseThread(Thread):
    '''Timelapse thread

    '''

    def __init__(self,camera:StillCamera, interval:int):
        self.cam = camera
        self.interval = interval

        self.running = True
        self.stopper = Event()

        logging.info("Starting timelapse")
        Thread.__init__(self)

    def run(self):
        while self.running:
            self.cam.capture()
            self.stopper.wait(self.interval)
        
    def stop(self):
        self.running = False
        self.stopper.set()
     

if __name__=='__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)

    from time import sleep

    picam = PiCamera()
    cam = StillCamera(picam)
    cam.start_timelapse(5)
    sleep(60)
    cam.stop_timelapse()
