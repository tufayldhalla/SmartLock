import sys, time

class Arduino():


    def __init__(self):
        print("boop")


    def read(self):
        arduino_input_header = str(input("HEADER: "))
        arduino_input = str(input("MSG: "))
        
        return arduino_input_header, arduino_input

    def write(self, angie):
        print(angie)
