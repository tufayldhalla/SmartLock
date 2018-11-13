# DEVICES MODULE

from components import config
import serial


"""
Arduino Handler Class
"""
class Arduino:    
    
    def __init__(self):
        
        self.serial = serial.Serial(config.arduino_serial_port, config.arduino_baud)    
    
    
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
    
    
    
"""
Print Reader Handler Class
"""
class PrintReader:
    
    def __init__(self, connection):
        
        self.connection = connection
        
    
    """
    Fingerprint Profile Definition
    """
    class FProfile:
        
        def __init__(self):
            pass