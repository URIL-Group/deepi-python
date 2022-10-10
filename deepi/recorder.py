#! /usr/bin/env python
""" Module for setting up a video recorder

"""

from time import sleep
from threading import Thread, Event
from itertools import count
import logging
from picamera import PiCamera

# TODO: seperate recorder from thread so that we can start and stop

class VideoRecorder:

    thread = None
    workingdir = '/home/pi/Videos/'

    def __init__(self,picam:PiCamera, splitter_port=1):
        self.picam = picam
        self.split_time = split_time
        self.port = splitter_port

    def start(self, split_time=None, threaded=False):
        self.thread = RecorderThread(self.picam,
                                     splitter_port=self.port,
                                     split_time=split_time)
        self.thread.start()

    def stop(self):
        pass

    def split(self):
        pass

    def toggle(self):
        pass

class RecorderThread(Thread):

    workingdir = '/home/pi/Videos/'
    
    def __init__(self,picam:PiCamera, splitter_port:int=1,
                 split_time:int=None):
        self.picam = picam
        self.split_time = split_time
        self.splitter_port = splitter_port
        self.recording = False
        Thread.__init__(self)

    def run(self):
        self.picam.start_recording(self.
            

    def run(self):
        num = 1
        self.recording = True
        output = self.workingdir+f'vid{num:04}'+'.h264'
        logging.debug(f"Starting recording: {output}")
        self.picam.start_recording(output,splitter_port=self.splitter_port)
        while self.recording and self.picam.recording:
            self.picam.wait_recording(self.split_time,
                                      splitter_port=self.splitter_port)
            num += 1
            output = self.workingdir+f'vid{num:04}'+'.h264'
            logging.debug(f"Splitting  recording: {output}")
            self.picam.split_recording(output,splitter_port=self.splitter_port)

    def stop(self):
        logging.debug("Stopping recording")
        self.picam.stop_recording(splitter_port=self.splitter_port)
        self.recording = False
        logging.debug("Waiting for recording thread to finish")
        self.join()
    

if __name__=="__main__":

    logging.basicConfig(format='%(levelname)s: %(message)s',level=logging.DEBUG)
    logging.info("Starting PiCamera")

    with PiCamera() as camera:
        sleep(2)
        
        logging.info("Starting recording")
        recorder = VideoRecorder(camera, splitter_port=1, split_time=10)
        recorder.start()
        
        try:
            while True:
                sleep(30)
        except KeyboardInterrupt:
            logging.info("Interruped by user")
            logging.info("Stopping recording")
            recorder.stop()
