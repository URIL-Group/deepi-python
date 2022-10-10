#! /usr/bin/env
"""Simple module to connect and LED and turn on/off

"""

import logging
from RPi import GPIO

LED_PIN = 12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class Lights:
    '''Class to control LED output through GPIO

    '''

    status = False

    def __init__(self, pin=LED_PIN):
        logging.debug(f"Initiaizing lights on pin {pin}.")
        GPIO.setup(LED_PIN,GPIO.OUT)
        self.pwm = GPIO.PWM(LED_PIN,1000)
        self.pwm.start(0)
        self.on()               # default is on in case no webapp

    def set(self,duty_cycle):
        # Set LED pwm between 0-100%
        logging.debug(f"Set LED duty cycle: {duty_cycle}")
        self.pwm.ChangeDutyCycle(duty_cycle)

    def on(self):
        # Set LED on
        self.status = True
        self.set(100)        

    def off(self):
        # Set LED off
        self.status = False
        self.set(0)        
        
    def toggle(self):
        # Toggle LED between on and off
        self.status = not self.status
        self.set(100*self.status)


if __name__=='__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                    level=logging.DEBUG)

    lights = Lights(12)
    from time import sleep

    while True:
        for dc in range(100):
            lights.set(dc)
            sleep(1)
