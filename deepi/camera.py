#! /usr/bin/env python3
''' Camera that can be controlled

'''

from picamera import PiCamera
from datetime import datetime

def timestamp(self):
    return datetime.now().strftime('%Y%m%d-%H%M%S.%f')

class DEEPiCamera(PiCamera):

    def __init__(self, resolution=(1920,1080), framerate=30, workingdir='deepi'):

        PiCamera.__init__(self,camera_num=0, stereo_mode='none',
                               stereo_decimate=False,
                               resolution=resolution, framerate=framerate,
                               sensor_mode=0, led_pin=None,
                               clock_mode='reset', framerate_range=None )
        # TODO: apply some settings

    def capture(self):
        output = workingdir+'/'+timestamp()+'.jpeg'
        PiCamera.capture(self,output, format=None,
                         use_video_port=False, resize=None, splitter_port=0,
                         bayer=False)

    def capture_continuous(self):
        output = workingdir+'/'+timestamp()+'.jpeg'
        PiCamera.capture_continuous(self,output, format=None,
                                    use_video_port=False, resize=None,
                                    splitter_port=0, burst=False,
                                    bayer=False)

    def capture_sequence(self):
        outputs = workingdir+'/'+timestamp()+'.jpeg'
        PiCamera.capture_sequence(self,outputs, format='jpeg',
                                  use_video_port=False, resize=None,
                                  splitter_port=0, burst=False,
                                  bayer=False)

    def start_recording(self):
        output = None
        Picamera.start_recording(self,output, format=None, resize=None,
                              splitter_port=1)

    def record_sequence(self):
        PiCamera.record_sequence(self,outputs, format='h264',
                                 resize=None, splitter_port=1)

    def split_recording(self):
        output = None
        PiCamera.split_recording(output, splitter_port=1, **options)


