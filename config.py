#! /usr/bin/env python
'''Open a configuration file and set up camera settings

'''

import yaml
import io

# TODO: add webapp for changing config

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

    
