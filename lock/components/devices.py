# Author: Martin Klamrowski
# Last modified: 5/12/2018

# DEVICES MODULE

from picamera import PiCamera
from components import config
import serial, time


class Arduino:
    """
    Arduino Handler Class.
    """    
    
    def __init__(self):
        """
        Constructor.
        
        Arduino.__init__() --> Arduino
        """
        self.serial = serial.Serial(port=config.arduino_serial_port,
                                    baudrate=config.arduino_baud,
                                    timeout=config.arduino_timeout)
        
    
    
    def write(self, data):
        """
        Write data string to serial port.
        
        Arduino.write(data) --> None
        """        
        self.serial.write(str(data).encode())
    
    
    
    def read(self):
        """
        Read serial port.
        
        Arduino.read() --> str
        """
        return (self.serial.readline().decode()).rstrip("\r\n")
    
    

class Camera:
    """
    Camera Handler Class.
    """    

    def __init__(self):
        """
        Constructor.
        
        Camera.__init__() --> Camera
        """        
        self.camera = PiCamera()
        self.num_pics = 0
        self.camera.resolution = config.camera_resolution



    def take_picture(self):
        """
        Take a picture with the RPi camera return the picture name.
    
        Camera.take_picture() --> int
        """
        time.sleep(1)
        self.num_pics += 1
        self.camera.capture('{}.png'.format(self.num_pics))

        return self.num_pics