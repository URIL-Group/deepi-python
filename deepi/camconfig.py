#! /usr/env/python3
'''Load camera config

'''

import os
from configparser import ConfigParser
import logging

def load(config_loc=None):
    '''Load camera config files

    If multiple files are found, all are read, but there is an order
    of operations that determines read order

    '''

    config = ConfigParser()

    # Read default
    config.read(os.path.join(os.path.dirname(__file__),'conf','default.conf'))

    # System configurations in order that overwrites
    locs = [os.curdir, "etc/deepi", os.path.expanduser("~")]
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
        config.read(fpath)

    return config
    
if __name__=='__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)

    config = load()

    print("======== All Sections ===============")
    for section_name, section in config.items():

        print(f"======== {section_name} ===============")
        for sec_key, sec_val in config.items(section_name):
            print("{:20s} - {}".format(sec_key, sec_val))
