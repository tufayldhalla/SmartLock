import time
from picamera import PiCamera


"""
Camera Handler Class
"""
class Camera:

    def __init__(self):

        self.camera = PiCamera()
        self.num_pics = 0

    def take_picture(self):

        time.sleep(1)
        self.camera.capture('{}.jpg'.format(self.num_pics))
        self.num_pics += 1
