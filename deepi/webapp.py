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
import camconfig

WS_PORT = 8081

template_dir = os.path.abspath('../resources/templates/')
static_dir   = os.path.abspath('../resources/static/')
app = Flask(__name__,
            static_url_path='', 
            static_folder=static_dir,
            template_folder=template_dir)

# Read Config file
logging.debug("Reading config file")
config = camconfig.get_default()
config = camconfig.load('../resources/deepi.conf')
logging.debug(f"Cam config: \n\n\
{yaml.dump(config, default_flow_style=False)}")

# Open camera
logging.debug("Opening camera")
camera = DEEPiCamera(config)
logging.info('Initializing camera')

# recorder = VideoRecorder(camera, splitter_port=1, split_time=10)
# timelapse = TimeLapse(camera,interval=5)

logging.info('Starting Stream')
streamer = WebSocketStream(camera, WS_PORT,
                           resolution=(640,480),
                           splitter_port=2)

camera.start_recording(streamer.output, 'yuv',
                       splitter_port=2,
                       resize=streamer.resolution)

@app.route('/')
def index():
    return render_template('index.html',wsport=WS_PORT)


if __name__ == "__main__":
    logging.debug(f"Camera recording: {camera.recording}")
    app.run(host='0.0.0.0',port=5000,debug=False)
