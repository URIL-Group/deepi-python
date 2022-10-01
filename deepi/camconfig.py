#! /usr/env/python3
'''Camera configuration modue

'''

import os
from configparser import ConfigParser
import logging

def load(config_loc:str=None) -> ConfigParser:
    '''Load camera config files

    If multiple files are found, all are read in order. Dupicate settings are
    overwritten in order of precedence.

    1. `config_loc` passed to function
    2. File defined by environmental variable DEEPI_CONF
    3. `./deepi.conf`
    4. `~/deepi.conf`
    5. `/etc/deepi/deepi.conf`
    6. Default settings

    '''

    config = ConfigParser()

    # Read default
    logging.debug("Reading default config")
    config.read(os.path.join(os.path.dirname(__file__),'conf','default.conf'))

    # System configurations in order that overwrites
    locs = ["etc/deepi", os.path.expanduser("~"), os.curdir]
    for loc in locs:
        try: 
            config.read( os.path.join(loc,"deepi.conf") )
            logging.debug(f"Reading config file: {loc}")
        except IOError:
            logging.debug(f"No config found at {loc}")

    if os.environ.get("DEEPI_CONF") is not None:
        # Reading environmental variable if set up
        logging.debug(f"Looking for config in {loc}")
        config.read( os.path.join(loc,"deepi.conf") )

    if config_loc is not None:
        # finally reading specified file
        logging.debug(f"Reading config file: {config_loc}")
        # TODO: check if it exists
        config.read(config_loc)

    return config
    


if __name__=='__main__':
    
    '''Test loading the default'''

    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)

    config = load('conf/default.conf')

    print("======== All Sections ===============")
    for section_name, section in config.items():

        print(f"======== {section_name} ===============")
        for sec_key, sec_val in config.items(section_name):
            print("{:20s} - {}".format(sec_key, sec_val))
