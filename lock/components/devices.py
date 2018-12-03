# DEVICES MODULE

from components import config
import serial


"""
Arduino Handler Class
"""
class Arduino:    
    
    def __init__(self):
        
        self.serial = serial.Serial(port=config.arduino_serial_port,
                                    baudrate=config.arduino_baud,
                                    timeout=config.arduino_timeout)    
    
    
    """
    write data string to serial port
    """
    def write(self, data):
        
        self.serial.write(str(data).encode())
    
    
    """
    read serial port and return data string
    """
    def read(self):
        
        return (self.serial.readline().decode()).rstrip("\r\n")
    
    
