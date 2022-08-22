IMAGE_DIR = '/home/pi/Pictures/'
VIDEO_DIR = '/home/pi/Videos/'

def timestamp():
    return datetime.now().strftime('%Y%m%d-%H%M%S.%f')

class DEEPiCamera(PiCamera):

    def __init__(self,config_file=None):
        

    def capture(self):

        output = IMAGE_DIR+f'{timestamp()}.jpeg'

        PiCamera.capture(self, output, format=None,
                         use_video_port=True, resize=None, splitter_port=0,
                         bayer=False)

    def start_recording(self):

        output = VIDEO_DIR+f'{timestamp()}.h264'

        PiCamera.start_recording(output, format=None, resize=None,
                                 splitter_port=1)

    def stop_recording(self):

        PiCamera.stop_recording(splitter_port=1)

    def start_streaming(self,resize=None):

        output = None           # TODO
        
        PiCamera.start_recording(output, format=None, resize=resize,
                                 splitter_port=2)

    def stop_streaming(self):

        PiCamera.stop_recording(splitter_port=2)

    
        
