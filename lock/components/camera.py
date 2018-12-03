import time
from picamera import PiCamera


"""
Camera Handler Class
"""
class Camera:

    def __init__(self):

        self.camera = PiCamera()
        self.num_pics = 0
        self.camera.resolution = (720, 480)

    def take_picture(self):

        time.sleep(1)
        self.num_pics += 1
        self.camera.capture('{}.png'.format(self.num_pics))

        return self.num_pics
        
        
