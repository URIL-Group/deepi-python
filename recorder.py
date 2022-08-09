from time import sleep
from threading import Thread, Event
from itertools import count

import logging

class VideoRecorder(Thread):

    workingdir = '/home/pi/Videos/'
    # TODO
    
    def __init__(self,picam, splitter_port=1, split_time=600):
        self.picam = picam
        self.split_time = split_time
        self.splitter_port = splitter_port
        self.recording = False
        Thread.__init__(self)

    def run(self):
        vidnum = 1
        self.recording = True
        while self.recording:
            output = workingdir+f'vid{num}'+'h264'
            self.picam.start_recording(output,splitter_port=self.splitter_port)
            self.picam.wait_recording(splitter_port=self.splitter_port)

    def stop(self):
        self.picam.stop_recording(splitter_port=self.splitter_port)
        self.recording = False
    

if __name__=="__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)

    logging.info("Starting PiCamera")
    from picamera import PiCamera
    picam = PiCamera()
    sleep(2)
    
    recorder = VideoRecorder(picam, splitter_port=1, split_time=10)
    recorder.start()

    sleep(30)

    recorder.stop()
