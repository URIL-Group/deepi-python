#! /usr/bin/env python
'''Web App module for DEEPi

'''

import os
from time import sleep
from flask import Flask, render_template, Response,redirect
import yaml
from datetime import datetime
from configparser import ConfigParser
from picamera import PiCamera
import logging

from picamera.mmalobj import to_resolution # in case config not using tuple

from deepi import WebSocketStream
from deepi import VideoRecorder, StillCamera


def make_web_streamer(picam:PiCamera, config:ConfigParser=None):
    '''Generate streamer using config

    '''
    logging.debug("Setting up stream")
    wsport = config.getint('WEBSTREAM','port')
    streaming_res = to_resolution(config.get('WEBSTREAM', 'resolution'))
    return WebSocketStream(picam, wsport, resolution=streaming_res,
                           splitter_port=2)


def make_camera(picam:PiCamera, config:ConfigParser=None):
    '''Generate camera using config

    '''
    logging.debug("Setting up still camera")
    outpath = config.get('STILLCAM','outpath')
    return StillCamera(picam, splitter_port=1, outpath=outpath)


def make_recorder(picam:PiCamera, config:ConfigParser=None):
    '''Generate recorder using config

    '''
    logging.debug("Seting up recorder")
    outpath = config.get('RECORDER', 'outpath')
    return VideoRecorder(picam, splitter_port=1, outpath=outpath)
    

def make_app(stillcam, recorder, streamer, lights):
    '''Generate flask app for user interface for the functionality

    '''

    streamer.start()
    lights.on()    

    webapp_path = os.path.join(os.path.dirname(__file__),'deepi','webapp')
    template_dir = os.path.join(webapp_path,'templates')
    static_dir   = os.path.join(webapp_path,'static')

    # template_dir = os.path.abspath('templates/')
    # static_dir   = os.path.abspath('static/')

    logging.debug("Building flask app")
    app = Flask(__name__,
                static_url_path='', 
                static_folder=static_dir,
                template_folder=template_dir)

    @app.route('/')
    def index():
        return render_template('index.html',wsport=streamer.ws_port)

    @app.route('/stream/')
    def stream_only():
        return render_template('stream.html',wsport=streamer.ws_port)

    @app.route('/capture/', methods=['POST'])
    def capture():
        try:
            stillcam.capture()
        except:
            logging.info("Captured failed")
            pass
        return redirect('/')    

    @app.route('/record_toggle/', methods=['POST'])
    def record_toggle():
        recorder.toggle()
        return redirect('/')

    # @app.route('/stream_toggle/', methods=['POST'])
    # def stream_toggle():
    #     streamer.toggle()
    #     return redirect('/')

    @app.route('/lights_toggle/', methods=['POST'])
    def lights_toggle():
        lights.toggle()
        return redirect('/')
    
    return app

if __name__ == "__main__":
    from deepi import DEEPiConfig
    from deepi import load_camera
    from deepi import PWMLightController as LightController
    from pathlib import Path

    # Config
    logging.debug("Reading config file")
    config = DEEPiConfig('deepi.conf')
    logpath = Path(config.get('ALL','logpath'))
    loglevel = config.get('ALL','loglevel') # TODO: get to work with config file

    logpath.mkdir(parents=True, exist_ok=True)
    log_file  = (logpath / datetime.utcnow().strftime('%Y%m%dT%H%M%S')).with_suffix('.txt')

    logging.debug("Reading config file")
    logging.info('Initializing camera')
    picam = load_camera(config)

    # Set up cameras
    stillcam = make_camera(picam, config)
    recorder = make_recorder(picam, config)
    streamer = make_web_streamer(picam, config)

    # Lights
    logging.debug("Starting lights")
    pin_num = config.getint('LIGHTS', 'gpio')
    lights = LightController(pin_num)

    # Generate app
    app = make_app(stillcam, recorder, streamer, lights)
    app.run(host='0.0.0.0',port=5000,debug=False)
