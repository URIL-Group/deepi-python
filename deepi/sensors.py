import csv
import time
import logging
import os
from pathlib import Path
from datetime import datetime
from threading import Thread

from kellerLD import KellerLD

from platform import node
HOSTNAME = node()

sampling_rate_Hz = 1
_dt = 1/sampling_rate_Hz


def timestamp() -> str:
    '''Return a simple timestamp for saving files
    '''
    return datetime.utcnow().isoformat()

class Bar100(KellerLD):

    label = ["Pressure (bar)", "Temperature (deg C)"]

    def __init__(self):
        KellerLD.__init__(self)
        if not KellerLD.init(self):
            logging.error("Failed to initialize Bar 100 sensor!")
            # TODO: need to handle this error
        time.sleep(3)

    def read(self):
        KellerLD.read(self)
        p = KellerLD.pressure(self)
        T = KellerLD.temperature(self)
        return [p,T]

class DataRecorder(Thread):

    def __init__(self, sensors, outdir:Path=Path.cwd(), sampling_rate:float=1):
        outdir.mkdir(parents=True, exist_ok=True) # create dir if not exists
        self.outdir = outdir
        self.sensors = sensors
        self._dt = 1/sampling_rate
        self.running = False
        Thread.__init__(self)

    @property
    def _output(self):
        return self.outdir / (timestamp()+HOSTNAME+'.csv')

    @property
    def sampling_rate(self):
        return 1/self._dt

    @sampling_rate.setter
    def sampling_rate(self,value):
        self._dt = 1/value

    @property
    def header(self):
        labels = ["Time"]
        [labels.extend([l for l in s.label]) for s in self.sensors]
        # NOTE: stacked list comprehension to handle multiple returns
        return labels

    def run(self):
        output = self._output
        logging.info(f"Opening data log file: {output}")
        with open(output, 'w') as f:
            log = csv.writer(f)
            
            log.writerow(self.header)
            logging.debug("Writing to data file")

            self.running = True
            logging.debug("Data recorder started")
            while self.running:
                try:
                    row = [timestamp()]
                    logging.debug(row)
                    [row.extend([x for x in s.read()]) for s in self.sensors]
                    # logging.debug(row)
                    # NOTE: stacked list comprehension to handle multiple returns
                    log.writerow(row)
                    time.sleep(self._dt)
                except Exception as e:
                    # TODO: handle error
                    logging.error(e)
            logging.debug("Data recorder stopped")

    def stop(self):
        logging.debug("Stopping data recorder")
        self.running = False

        
if __name__=='__main__':    
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG)


    from configparser import ConfigParser
    config = ConfigParser()
    sec = 'SENSORS'
    oudir = Path(config.get(sec, 'outpath'))
    if config.getboolean(sec, 'bar100'):
        sensor = Bar100()
    sampling_rate_Hz = config.getfloat(sec,'sampling_rate_Hz')

    data_recorder = DataRecorder([sensor], outdir, sampling_rate_Hz)

    T = 5
    data_recorder.start()
    logging.info(f"Running for {T} seconds")
    time.sleep(10)
    data_recorder.stop()
    data_recorder.join()