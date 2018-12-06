# Author: Angie Byun


"""
To simulate PiCamera. 
"""

class Camera():

    def __init__(self):
        self.num_pics= 0

    def takePicture(self):
        # if the number of picture is less than 5, increment
        if self.num_pics < 5:
            self.num_pics += 1

        # open image file
        filename = "{}.png".format(self.num_pics)
        file = open(filename, 'rb')
        
        return self.num_pics
    
        

       
