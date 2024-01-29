
import os
from time import sleep
from flask import Flask, render_template, Response,redirect
import yaml
from datetime import datetime
from configparser import ConfigParser
import logging
from pathlib import Path

# from deepi import WebSocketStream
# from deepi import VideoRecorder, StillCamera

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
    return render_template('index.html',wsport=8000)

@app.route('/stream/')
def stream_only():
    return render_template('stream.html',wsport=8000)

# Config
logging.debug("Reading config file")
# config = DEEPiConfig()
# logpath = Path(config.get('ALL','logpath'))
loglevel = logging.DEBUG # TODO: get to work with config file

logging.basicConfig(format='%(levelname)s: %(message)s',
                level=logging.DEBUG)

logging.debug("Reading config file")
logging.info('Initializing camera')
# picam = load_camera(config)

# Set up cameras
# stillcam = make_camera(picam, config)
# recorder = make_recorder(picam, config)
# streamer = make_web_streamer(picam, config)

# Lights
logging.debug("Starting lights")
# pin_num = config.getint('LIGHTS', 'gpio')
# lights = LightController(pin_num)

# Generate app
app.run(host='0.0.0.0',port=8080,debug=False)
