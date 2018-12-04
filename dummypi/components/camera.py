class Camera():

    def __init__(self):
        self.num_pics= 0

    def take_picture(self):

        if self.num_pics < 5:
            self.num_pics += 1
            
        filename = "{}.png".format(self.num_pics)
        file = open(filename, 'rb')
        
        return self.num_pics
    
        

       
