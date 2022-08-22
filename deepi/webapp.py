from time import sleep
import picamera
from flask import Flask, render_template, Response
import logging
import os

from .streaming import WebSocketStream


WS_PORT = 8081

if __name__ == "__main__":
    # NOTE: normally this would go at the bottom but flask acts weird
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)


logging.info('Initializing camera')
camera = picamera.PiCamera()

camera.resolution = (1280,720)
camera.framerate = 30
camera.vflip = True
camera.hflip = False 
sleep(1) # camera warm-up time

logging.info('Starting websockets thread')
streaming_resolution = (640,480)
streamer = WebSocketStream(camera, WS_PORT,
                           resolution=streaming_resolution,
                           splitter_port=2)

logging.info('Starting recording')
camera.start_recording(streamer.output, 'yuv', splitter_port=2,
                       resize=streaming_resolution)
        
template_dir = os.path.abspath('../resources/templates/')
static_dir   = os.path.abspath('../resources/static/')

app = Flask(__name__,
            static_url_path='', 
            static_folder=static_dir,
            template_folder=template_dir)


@app.route('/')
def index():
    return render_template('index.html',wsport=WS_PORT)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=False)
