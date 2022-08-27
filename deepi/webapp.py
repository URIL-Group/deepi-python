import os
from time import sleep
from flask import Flask, render_template, Response
import logging
import yaml

logging.basicConfig(format='%(levelname)s: %(message)s',
                    level=logging.DEBUG)

from streaming import WebSocketStream
from timelapse import TimeLapse
from recorder import VideoRecorder
from deepicamera import DEEPiCamera

from picamera.mmalobj import to_resolution

import camera 
import camconfig

logging.debug("Reading config file")
config = camconfig.load('conf/webapp.conf')

wsport = config.getint('STREAM','port')
streaming_resolution = to_resolution(config.get('STREAM','resolution'))
logging.debug(f"Streaming resolution: {streaming_resolution}")

template_dir = os.path.abspath('templates/')
static_dir   = os.path.abspath('static/')

app = Flask(__name__,
            static_url_path='', 
            static_folder=static_dir,
            template_folder=template_dir)

# Open camera
logging.debug("Opening camera")
#camera = DEEPiCamera(config)
logging.info('Initializing camera')
camera = camera.BaseCamera(config)
picam = camera._picam

# recorder = VideoRecorder(camera, splitter_port=1, split_time=10)
# timelapse = TimeLapseCamera(camera,interval=5)

logging.info('Starting Stream')
streamer = WebSocketStream(picam, wsport,
                           resolution=streaming_resolution,
                           splitter_port=2)

picam.start_recording(streamer.output, 'yuv',
                       splitter_port=2,
                       resize=streamer.resolution)

@app.route('/')
def index():
    return render_template('index.html',wsport=wsport)

@app.route('/stream/')
def stream_only():
    return render_template('stream.html',wsport=wsport)

@app.route('/capture/', methods=['POST'])
def capture():
    image_dir = os.path.join(os.path.expanduser("~"),'Pictures')
    picam.capture('

if __name__ == "__main__":
    logging.debug(f"Camera recording: {picam.recording}")
    app.run(host='0.0.0.0',port=5000,debug=False)
