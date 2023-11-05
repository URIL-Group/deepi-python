#!/usr/bin/env python3
'''' Refactor of code

'''
import logging
from pathlib import Path
from datetime import datetime
from threading import Thread
from time import sleep

def get_dtg() -> str:
    return datetime.now().isoformat()

from picamera import PiCamera
class PiCamera:
    '''Fake PiCamera class for testing'''

    resolution:tuple[int,int] = (1920,1080)

    def capture(self, output:Path):
        logging.info(f"Captured frame to {output}")

    def start_recording(self, output:Path, splitter_port=None):
        logging.info(f"started recording to {output} on splitter port: {splitter_port}")

    def stop_recording(self, splitter_port=None):
        logging.info(f"Stopped recording on splitter port: {splitter_port}")

try:
    from picamera import PiCamera
except: 
    logging.warning("picamera module not available. Using the fake one")
    
_picam = PiCamera()    

class Recorder:
    '''Base recorder class'''
    
    def __init__(self, picam:PiCamera, splitter_port:int):
        self._picam:PiCamera = picam
        self.splitter_port:int = splitter_port

    def start(self, output=None):
       self._picam.start_recording(output, splitter_port=self.splitter_port)

    def stop(self):
        self._picam.stop_recording(splitter_port=self.splitter_port)


class VideoRecorder(Recorder):
    '''Record video to file'''

    _fmt = ".h264"

    def __init__(self, picam:PiCamera, save_dir:Path=Path(".")):
        Recorder.__init__(self,picam, splitter_port=0)
        self.save_dir = save_dir

    @property
    def output(self) -> Path:
        return self.save_dir / f"{get_dtg()}.{fmt}"
    

class TimelapseThread(Thread):
    pass

class TimelapseRecorder(Recorder):

    thread:TimelapseThread = None

    def __init__(self, picam):
        Recorder.__init__(self,picam,splitter_port=1)

    def start(self):
        pass


class Streamer(Recorder):
    def __init__(self, picam):
        Recorder.__init__(self,picam)


from socket import socket, SOL_SOCKET, SO_REUSEADDR
class SocketOuput(socket):
    def __init__(self, addr:str='0.0.0.0', port:int=8000):
        socket.__init__(self)
        self.setsockopt(SOL_SOCKET, SO_REUSEADDR)
        self.addr = addr
        self.port = port

        self.bind(self.addr, self.port)
    

class SocketStreamer(Streamer):
    
    _picam:PiCamera
    output: SocketOuput


class WebsocketStreamer(Streamer):
    pass


class DEEPiCamera:
    '''Controller class for the DEEPi Camera'''    

    def __init__(self):

        self.picam:PiCamera = PiCamera()
        self.recorder:VideoRecorder = VideoRecorder(self.picam)
        self.timelapse:TimelapseRecorder = TimelapseRecorder(self.picam)
        self.streamer:Streamer = None

        config = None

    def load_config(self, f:Path) -> None:
        pass

    def save_config(self, f:Path) -> None:
        pass


if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.info("deepicamera.py started")

    deepi = DEEPiCamera()
    deepi.recorder.start()
    sleep(1)
    deepi.recorder.stop()

    logging.info("deepicamera.py complete")
