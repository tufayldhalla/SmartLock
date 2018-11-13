import socket, time, serial, sys
from components.camera import Camera
from components.devices import Arduino
from components.devices import PrintReader
from components import config

"""
DoorLock Class (RPi3)
"""
class DoorLock:
    
    def __init__(self):
        
        # device setup
        self.camera = Camera()
        self.print_reader = PrintReader(config.print_reader_connection)
        self.arduino = Arduino()        
                
        # server connection setup
        SERVER_ADDRESS = '192.168.0.21'
        PORT = 2018

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((SERVER_ADDRESS, PORT))
            
    def run(self):
        print("DEBUG: running")
        
        while True:
            print("DEBUG: enter pin my guy")            
	    
            try:
                arduino_input_header, arduino_input = (self.arduino.read()).split('\x00')
                #arduino_input_header = str(input())
                #arduino_input = str(input())

                try:
                    if arduino_input_header == "DATA":
                        if arduino_input == "WAKE":
                            # $ wake the reader (not implemented yet)
                            pass
                    
                        elif arduino_input == "BUZZ":
                            # $ buzz the owner
                            pass
                        
                        else:
                            # a PIN was sent by the Arduino
                            self.socket.sendall(self.make_bytes_packet("CMD", "PIN CHECK"))
                            
                            response = self.socket.recv(4096)
                            #print(response)
                            
                            if response:
                                response_header, response_str = response.decode().split('\x00')
                                
                                if response_header == "ACK" and response_str == "PIN CHECK":
                                    # ready to send PIN to server
                                    self.socket.sendall(self.make_bytes_packet("DATA", arduino_input))
                                    
                                    pin_check = self.socket.recv(4096)
                                    
                                    if pin_check:
                                        pin_check_header, pin_check_str = pin_check.decode().split('\x00')
                                        
                                        if pin_check_header == "DATA":
                                            if pin_check_str == "PIN CHECK FAIL":
                                                #print("step off bitch, that pin wrong yo.")
                                                self.arduino.write("AD" + "step off bitch")
                                            
                                            else:
                                                # PIN was good
                                                #print("welcome {}.".format(pin_check_str))
                                                self.arduino.write("AG" + pin_check_str)
                                                
                                                self.camera.takePicture()
                                                
                                        else:
                                            raise Exception("UNKNOWN DATA RECEIVED FROM SERVER")
                            
                                elif response_header == "ERROR":
                                    raise Exception("AN ERROR PACKET WAS RECEIVED:: {}".format(response_str))  
                                
                                else:
                                    raise Exception("UNKNOWN DATA RECEIVED FROM SERVER")                                
                                   
    
                except Exception as err:
                    #socket.close()
                    print(err)
                    continue
            
            
            except KeyboardInterrupt:
                sys.exit(0)            
            

    """
    make an packet guy
    """
    def make_bytes_packet(self, type, data):
        
        return ("{}\x00{}".format(type, data)).encode()
