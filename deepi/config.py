#! /usr/bin/env python
'''Open a configuration file and set up camera settings

'''

import yaml
import io

# TODO: add webapp for changing config

# Options
AWB_MODES
CAMERA_CAPTURE_PORT
CAMERA_PREVIEW_PORT
CAMERA_VIDEO_PORT
CAPTURE_TIMEOUT
CLOCK_MODES
DEFAULT_ANNOTATE_SIZE
DRC_STRENGTHS
EXPOSURE_MODES
FLASH_MODES
IMAGE_EFFECTS
ISO
MAX_FRAMERATE
MAX_RESOLUTION
METER_MODES
RAW_FORMATS
STEREO_MODES

# Overlays
overlays
add_overlay
remove_overlay
annotate_background
annotate_foreground
annotate_frame_num
annotate_text
annotate_text_size

# preview options
preview
preview_alpha
preview_fullscreen
preview_layer
preview_window

# Camera functions
capture
capture_continuous
capture_sequence
record_sequence
start_preview
stop_recording
start_recording
split_recording
wait_recording
stop_preview
request_key_frame
close

# Status
closed
recording
previewing
revision
analog_gain
digital_gain
frame

# read only
exposure_speed
timestamp

# Basic Settigns
hflip
vflip
rotation
resolution
framerate
framerate_delta
framerate_range
zoom
crop

# Manual Settings
sensor_mode
iso
shutter_speed
exposure_mode
exposure_compensation
brightness
contrast
saturation
sharpness

# After Effects
awb_mode
awb_gains
color_effects                   # tupel
drc_strength
image_denoise
image_effect
image_effect_params

# Advanced Settings
video_denoise
video_stabilization
exif_tags
clock_mode
still_stats
meter_mode
raw_format

# Flash
led
flash_mode





def get_default():
    config = {
        'resolution':(1920,1080),
        'framerate':30,
        'rotation':0,
        'vflip': False,
        'hflip': False,
    }
    
    return config
    

def get(picam=None):
    '''Read configuration from an open picamera

    '''

    if picam is None:           # FIXME: For debugging, get rid of
        config = {
            'resolution':(1920,1080),
            'framerate':30,
            'rotation':0,
            'vflip': False,
            'hflip': False,}
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


def load(fname):
    '''Load configuration from a file

    Files are in yaml format

    '''

    with open("test.conf", 'r') as stream:
        config = yaml.safe_load(stream)

    return config


def save(config, fname="camconfig.conf"):
    '''Save configuration to file

    '''
    if type(config['resolution']) is tuple:
        # print("correcting tuple")
        config['resolution'] = f"{config['resolution'][0]}x{config['resolution'][1]}"
        
    with io.open(fname, 'w', encoding='utf8') as outfile:

        outfile.write("# Camera Config\n")
        
        yaml.dump(config, outfile, default_flow_style=False,
                  allow_unicode=True)


def validate(config):
    '''Check if config values are valid
    
    '''
    return True


if __name__=='__main__':

    print("Creating config")
    # camconfig = { 'name':"test", 'resolution':[1920,1980] }
    camconfig = get(picam=None)
    print("Writing config to file")
    save(camconfig, "test.conf")

    print("Loading config from file")
    loaded_camconfig = load("test.conf")
    assert(camconfig == loaded_camconfig)
    print()
    print("Camera Config:")
    print(yaml.dump(camconfig, default_flow_style=False))

    
