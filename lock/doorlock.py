import socket
from components.camera import Camera
from components.fingerprint import PrintReader
from components.devices import Arduino
from components import config

"""
DoorLock Class (RPi3)
"""
class DoorLock:
    
    def __init__(self):
        
        self.camera = Camera(config.camera_connection)
        self.print_reader = PrintReader(config.print_reader_connection)
        self.arduino = Arduino()        
        self.server_address = None
        self.socket = None
        
        