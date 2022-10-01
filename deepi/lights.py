#! /usr/bin/env

import logging
from RPi import GPIO

LED_PIN = 12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


class Lights:

    status = False

    def __init__(self, pin=LED_PIN):
        logging.debug(f"Initiaizing lights on pin {pin}.")
        GPIO.setup(LED_PIN,GPIO.OUT)
        self.pwm = GPIO.PWM(LED_PIN,1000)
        self.pwm.start(0)
        self.on()               # default is on in case no webapp

    def set(self,duty_cycle):
        logging.debug(f"Set LED duty cycle: {duty_cycle}")
        self.pwm.ChangeDutyCycle(duty_cycle)

    def on(self):
        self.status = True
        self.set(100)        

    def off(self):
        self.status = False
        self.set(0)        
        
    def toggle(self):
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