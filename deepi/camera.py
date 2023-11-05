#! /usr/bin/env python
'''
The camera module contains wrappers for the PiCamera class that automates portions for DEEPi.

'''

import logging
import os
from pathlib import Path
from time import sleep
from datetime import datetime
from threading import Thread, Event

from configparser import ConfigParser

from picamera import PiCamera

# TODO: make sure these directories exist
# TODO: put these in the config

def timestamp() -> str:
    '''Return a simple timestamp for saving files
    '''
    #return datetime.now().strftime('%Y%m%dT%H%M%S')
    return datetime.utcnow().isoformat()

class VideoRecorder:
    '''Recorder for video
    '''

    def __init__(self, picam:PiCamera, splitter_port:int=1,
                 outpath:str=os.curdir, format:str='h264'):

        self.recording = False
        self.picam:PiCamera = picam
        self.splitter_port = splitter_port
        self.save_dir = outpath
        self.save_fmt = format

    @property
    def _output(self):
        return os.path.join(self.save_dir,timestamp()+'.'+self.save_fmt)

    def start(self):
        '''Create an output file and start recording to it. The output file depends on the format used by the recorder and save directory'''
        self.picam.start_recording(self._output, splitter_port=self.splitter_port)
        self.recording = True
        logging.info(f"Recording to {self._output}")

    def wait(self, interval):
        self.picam.wait_recording(interval, splitter_port=self.splitter_port)

    def split(self):
        logging.info(f"Splitting recording to {self._output}")
        self.picam.split_recording(self._output, splitter_port=self.splitter_port)
        self.recording = True

    def toggle(self):
        if self.recording:
            self.stop()
        else:
            self.start()            

    def stop(self):
        if self.recording:
            logging.info("Stopping recording")
            self.picam.stop_recording(splitter_port=self.splitter_port)
            self.recording = False
        else:
            logging.debug("Recording already stopped")


class RecorderThread(Thread):
    '''Thread to keep video going in the backaground. The recording thread uses the methods from the VideoRecorder class to split the recording at regular intervals.

    The RecorderThread inherets from the standard python threading.Thread class. It modifies the constructor and the methods for run and stop.
    '''

    def __init__(self, recorder:VideoRecorder, interval:int):
        self.rec:VideoRecorder = recorder
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
    ''' Simple camera for taking photos. It automatically creates captures with timestamped files of the specified format in the specified directory.
    '''

    def __init__(self, picam:PiCamera, splitter_port:int=1,
                 outpath:Path=os.curdir, fmt:str='jpeg'):
        self.picam:PiCamera = picam
        self.splitter_port = splitter_port
        self.save_dir = outpath
        self.fmt = fmt
        self.timelapse:Thread = None

    @property
    def _output(self) -> Path:
        '''Generate the output file as a path'''
        return os.path.join(self.save_dir,timestamp()+'.'+self.fmt)

    def capture(self):
        '''Capture a single image using standard settings. The output file path is also auto generated and timestamped.'''
        # TODO: include an option to not use the video port. The video_port is the standard because it is much faster. When it is not used, the camera takes a moment to determine new settings. It also interupts any video being recorded.
        logging.info(f"Capturing to {self._output}")
        self.picam.capture(self._output, use_video_port=True,
                           splitter_port=self.splitter_port)

    def start_timelapse(self,interval:int=600):
        '''Spawns a timelapse thread and begins captures at a set interval using the settings from the base camera object. If the class already has a timelapse instance, the instance is stopped an a new one is created.'''
        if self.timelapse is not None:
            self.timelapse.stop()
        self.timelapse = TimelapseThread(self.picam, interval)
        self.timelapse.start()

    def stop_timelapse(self):
        '''Stop the current timelapse instance.'''
        if self.timelapse is None:
            return
        self.timelapse.stop()
        self.timelapse.join()
        self.timelapse = None


class TimelapseThread(Thread):
    '''Timelapse thread based on the standard python threading library's Thread class. The constructor and methods for run and stop are modified to 

    '''

    def __init__(self,camera:StillCamera, interval:int):
        self.camera:StillCamera = camera
        self.interval = interval

        self.running = True
        self.stopper = Event()

        logging.info("Starting timelapse")
        Thread.__init__(self)

    def run(self):
        while self.running:
            self.camera.capture()
            self.stopper.wait(self.interval)
        
    def stop(self):
        self.running = False
        self.stopper.set()
        self.join()
     
# TODO: CameraConfig should be a class 
class DEEPiConfig(ConfigParser):
    '''Defines the camera configuration which is defined by a configuration file. The configuration can load a default file which is included in the python package.'''

    _default_config_file:Path = os.path.join(os.path.dirname(__file__),
                                       'conf','default.conf')

    def __init__(self, loc:Path=None):
        ConfigParser.__init__(self)
        logging.debug("Reading from default configuration")
        self.read(self._default_config_file)
        if loc is not None:
            logging.debug(f"Overwriting settings using config: {loc}.")
            self.read(loc)
            self.f:Path = loc

        self.load()


def load_camera(config:ConfigParser=None) -> PiCamera: 
    '''Load the Raspberry Pi camera and select settings'''

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



if __name__=='__main__':

    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)

    config = DEEPiConfig('conf/default.conf')

    print("======== All Sections ===============")
    for section_name, section in config.items():

        print(f"======== {section_name} ===============")
        for sec_key, sec_val in config.items(section_name):
            print("{:20s} - {}".format(sec_key, sec_val))

    picam = load_camera(config)
    cam = StillCamera(picam)
    cam.start_timelapse(5)
    sleep(60)
    cam.stop_timelapse()
