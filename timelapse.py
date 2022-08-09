from time import sleep
from threading import Thread, Event

import logging

class TimeLapse(Thread):

    workingdir = '/home/pi/Pictures/'
    # TODO: working directory (ensure exists)

    def __init__(self,picam,interval):

        self.picam = picam
        self.interval = interval

        self._exit = Event()
        
        Thread.__init__(self)

    def run(self):
        for fname in camera.capture_continuous(self.workingdir +
                                               f'img{counter:03d}.jpg'):
            logging.debug(f"Taking picture {fname}")
            self._exit.wait(self.interval)
            if self._exit.is_set():
                logging.debug("Stop signal recieved")
                break

    def stop(self):
        logging.debug("Sending stop signal")
        self._exit.set()
        self.join()
        logging.debug("Thread complete")


if __name__=="__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s',level=logging.DEBUG)

    logging.info("Starting PiCamera")
    from picamera import PiCamera
    picam = PiCamera()
    sleep(2)

    timelapse = TimeLapse(picam,interval=5)
    logging.info("Starting timelapse")
    timelapse.start()

    sleep(30)

    logging.info("Stopping timelapse")
    timelapse.stop()

    # TODO: check to see if it worked
