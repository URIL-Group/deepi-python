'''Control module for DEEPi

Russ Shomberg, URI, 2022
'''

import datetime
from time import sleep

import yaml
from yaml.loader import SafeLoader

def timestamp(self):
    return datetime.now().strftime('%Y%m%d-%H%M%S.%f')


def init_camera(config=None):

    from picamera import PiCamera
    picam = PiCamera()

    if config is not None:
        pass                    # TODO

    while not picam


if __name__=="__main__":

    # TODO: Start logging

    # TODO: Test camera access

    # TODO: Open config file

    # TODO: start streaming socket server (only open 

    # TODO: 

