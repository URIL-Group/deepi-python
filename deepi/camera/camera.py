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
    #return datetime.now().strftime('%Y%m%dT%H%M%S')
    return datetime.utcnow().isoformat()

class VideoRecorder:
    '''Recorder for video

    '''


    def __init__(self, picam:PiCamera, splitter_port:int=1,
                 outpath:str=os.curdir, fmt='h264'):

        self.recording = False
        self.picam = picam
        self.port = splitter_port
        self.path = outpath
        self.fmt = fmt

    @property
    def output(self):
        return os.path.join(self.path,timestamp()+'.'+self.fmt)

    def start(self):
        self.picam.start_recording(self.output, splitter_port=self.port)
        self.recording = True
        logging.info(f"Recording to {self.output}")

    def wait(self, interval):
        self.picam.wait_recording(interval, splitter_port=self.port)

    def split(self):
        logging.info(f"Splitting recording to {self.output}")
        self.picam.split_recording(self.output, splitter_port=self.port)
        self.recording = True

    def toggle(self):
        if self.recording:
            self.stop()
        else:
            self.start()            

    def stop(self):
        if self.recording:
            logging.info("Stopping recording")
            self.picam.stop_recording(splitter_port=self.port)
            self.recording = False
        else:
            logging.debug("Recording already stopped")


class RecorderThread:
    '''Thread to keep video going

    '''

    def __init__(self, recorder:VideoRecorder, interval):
        self.rec = recorder
        self.interval = interval

        self.running = False
        Thread.__init__(self)
        #Thread.start(self)

    def run(self):
        logging.debug("Recorder thread starting")
        self.rec.start()
        self.running = True
        while self.running and self.rec.recording:
            self.rec.wait(self.interval)
            self.rec.split()

    def stop(self):
        self.rec.stop()
        self.running = False
        self.join()
        


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
        self.join()
     

if __name__=='__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)

    from time import sleep

    picam = PiCamera()
    cam = StillCamera(picam)
    cam.start_timelapse(5)
    sleep(60)
    cam.stop_timelapse()
