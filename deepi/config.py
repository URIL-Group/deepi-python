#! /usr/bin/env python
'''Open a configuration file and set up camera settings

'''

import yaml
import io

# from picamera import PiCamera

def get_default():
    config = {
        # Modes
        'timelapse': False,
        'timelapse_interval': 0
        'recorder': False,
        'recorder_interval': 600

        # Basic settings
        'resolution':(1920,1080),
        'framerate':30,

        # Position
        'rotation':0,
        'vflip': False,
        'hflip': False,

        # Camera Setting
        'iso': 0,
        'shutter_speed': 0,
        'exposure_mode': 0,

        # After Camera
        'brightness': 0,
        'contrast': 0,
        'saturation': 0,
        'sharpness': 0,

        # Flash Settings
        'led': False,
        'flash_mode': 'off',
    }
    
    return config
    

def get(picam=None):
    '''Read configuration from an open picamera

    '''

    if picam is None:           # FIXME: For debugging, get rid of
        config = get_default()
        return config

    config = {
        'resolution':f'{picam.resolution[0]}x{picam.resolution[1]}',
        'framerate':picam.framerate,
        'rotation':picam.rotation }

    return config


def set(picam, config):
    '''Apply a configuration to a camera

    '''
    if picam.recording:
        # raise CameraBusyError
        return False

    picam.resolution = config['resolution']
    picam.framerate = config['framerate']


def load(fpath):
    '''Load configuration from a file

    Files are in yaml format

    '''

    with open(fpath, 'r') as stream:
        config = yaml.safe_load(stream)

    return config


def save(config, fpath="camconfig.conf"):
    '''Save configuration to file

    '''
    if type(config['resolution']) is tuple:
        # print("correcting tuple")
        config['resolution'] = f"{config['resolution'][0]}x{config['resolution'][1]}"
        
    with io.open(fpath, 'w', encoding='utf8') as outfile:

        outfile.write("# Camera Config\n")
        
        yaml.dump(config, outfile, default_flow_style=False,
                  allow_unicode=True)


def validate(config):
    '''Check if config values are valid
    
    '''
    return True


# PiCamera.AWB_MODES
# PiCamera.CAMERA_CAPTURE_PORT
# PiCamera.CAMERA_PREVIEW_PORT
# PiCamera.CAMERA_VIDEO_PORT
# PiCamera.CAPTURE_TIMEOUT
# PiCamera.CLOCK_MODES
# PiCamera.DEFAULT_ANNOTATE_SIZE
# PiCamera.DRC_STRENGTHS
# PiCamera.EXPOSURE_MODES
# PiCamera.FLASH_MODES
# PiCamera.IMAGE_EFFECTS
# PiCamera.MAX_FRAMERATE
# PiCamera.MAX_RESOLUTION
# PiCamera.METER_MODES
# PiCamera.RAW_FORMATS
# PiCamera.STEREO_MODES

if __name__=='__main__':

    fpath = '../resources/test.conf'
    print("Creating config")
    camconfig = get(picam=None)
    print("Writing config to file")
    save(camconfig, fpath)

    print("Loading config from file")
    loaded_camconfig = load(fpath)
    assert(camconfig == loaded_camconfig)
    print()
    print("Camera Config:")
    print(yaml.dump(camconfig, default_flow_style=False))

    
