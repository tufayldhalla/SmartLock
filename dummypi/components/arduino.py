# Author: Angie Byun

import sys, time


"""
To simulate Arduino.
"""
class Arduino():

    
    def __init__(self):
        print("boop")

    # Arduino input for HEADER and MSG
    def read(self):
        arduino_input_header = str(input("HEADER: "))
        arduino_input = str(input("MSG: "))
        
        return arduino_input_header, arduino_input

    # Print statement 
    def write(self, angie):
        print(angie)
