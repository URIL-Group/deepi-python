#! /usr/bin/env
"""Simple module to connect and LED and turn on/off

"""

import logging
from RPi import GPIO

LED_PIN = 12
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class LightController:
    '''
    Base class for controlling the lights. There can be multiple implimentations of this class which much impliment methods for `setup`, `on`, and `off`
    '''
    status:bool
    def __init__(self, status:bool=True):
        logging.debug(f"Initializing lights.")
        if status:
            self.on()
        else:
            self.off()
        self.status = status

    def on(self):
        raise NotImplementedError
    
    def off(self):
        raise NotImplementedError
    
    def toggle(self):
        if self.status:
            self.off()
        else:
            self.on()


class GPIOLightController(LightController):
    '''Light Controller using a GPIO input with high and low functionality'''

    def __init__(self, pin_num:int=LED_PIN, status:bool=True):
        self.pin_num = pin_num
        GPIO.setup(self.pin_num, GPIO.OUT)
        LightController.__init__(self, status=True)

    def on(self):
        logging.debug(f"Setting pin {self.pin_num} high.")
        GPIO.output(self.pin_num, GPIO.HIGH)
        self.status = True

    def off(self):
        logging.debug(f"Setting pin {self.pin_num} low.")
        GPIO.output(self.pin_num, GPIO.HIGH)
        self.status = False


class PWMLightController(LightController):
    '''Controls the lights using a PWM. The PWM can be used as the input for a LED driver allowing for dimming of the LED. The `pwm_val` is a float between `0.0` and `100.0`. '''

    def __init__(self, pin_num:int=LED_PIN, status:bool=True, 
                 duty_cycle:float=100.0):
        self.pin_num = pin_num
        self._duty_cycle = duty_cycle
        GPIO.setup(self.pin_num, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin_num, self.duty_cycle)
        self.pwm.start(self.duty_cycle)
        LightController.__init__(self, status=True)

    def on(self, val:float=None):
        '''When turned on, the pwm is set to the previous value.'''
        if val is not None:
            self._duty_cycle = val
        logging.debug(f"Setting pin {self.pin_num}"
                      f"to pin pwm value {self.duty_cycle}")
        self.pwm.ChangeDutyCycle(self.duty_cycle)
        self.status = True

    def off(self, val:float=0):
        '''When turned on, the pwm is set to the previous value.'''
        logging.debug(f"Setting pin {self.pin_num}"
                      f"to pin pwm value {val}")
        self.pwm.ChangeDutyCycle(val)
        self.status = False

    @property
    def duty_cycle(self)->float:
        return self._duty_cycle
    
    @duty_cycle.setter
    def duty_cycle(self, val:float):
        '''When the `duty_cycle` of the object is changed, the duty cycle of the pin is changed as well.'''
        self._duty_cycle = val



if __name__=='__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s',
                    level=logging.DEBUG)

    from time import sleep

    lights = PWMLightController(12)

    while True:
        for dc in range(100):
            lights.duty_cycle(dc)
            sleep(1)
