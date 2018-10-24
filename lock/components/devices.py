# DEVICES MODULE

from components import config


"""
Arduino Handler Class
"""
class Arduino:    
    
    def __init__(self):
        
        self.lcd = LCD(config.lcd_pins)
        self.keypad = Keypad(config.keypad_pins)
        self.stepper = Stepper(config.stepper_pins)
        
        
"""
Keypad Handler Class
"""
class Keypad:
    
    def __init__(self, pins):
        
        self.pins = pins
        
        
"""
LCD Handler Class
"""
class LCD:
    
    def __init__(self, pins):
        
        self.pins = pins
    

"""
Stepper Handler Class
"""
class Stepper:
    
    def __init__(self, pins):
        
        self.pins = pins
    