import socket, time, serial, sys, logging
from components.camera import Camera
from components.devices import Arduino
from components.devices import PrintReader
from components import config

"""
DoorLock Class (RPi3)
"""
class DoorLock:
    
    def __init__(self, ID, debug, testing):
        

        # device setup
        self.camera = Camera()
        self.print_reader = PrintReader(config.print_reader_connection)
        self.debug = debug
        self.testing = testing
        self.formatter = logging.Formatter("\%(asctime)s \%(levelname)s \%(identifier)s \%(message)s\n")
        self.ID = ID

        if self.debug == 'n':
            self.arduino = Arduino()        
                
        # server connection setup
        SERVER_ADDRESS = '192.168.0.21'
        PORT = 2018
        
        if self.testing == 'n':
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((SERVER_ADDRESS, PORT))
            


    def run(self):
        
        while True:
            try: # check for exit    

                ################################### ARDUINO ###################################


                try:
                    if self.debug == 'n':
                        arduino_input_header, arduino_input = (self.arduino.read()).split('&')
                    
                    else:
                        print("DEBUG: running")
                        print("DEBUG: enter pin my guy")
                        arduino_input_header = str(input("HEADER: "))
                        arduino_input = str(input("MSG: "))
                    print(arduino_input)
                    print(len(arduino_input))

                    
                    if arduino_input_header == "DATA":
                        if arduino_input == "WAKE":
                            # $ wake the reader (not implemented yet)
                            pass
                    
                        elif arduino_input == "BUZZ":
                            # $ buzz the owner
                            self.buzz_subroutine()
                        
                        else:

                            # a PIN was sent by the Arduino
                            self.socket.sendall(self.make_packet("CMD", "PIN CHECK"))
                            
                            response = self.socket.recv(4096)
                            #print(response)
                            
                            if response:
                                response_header, response_str, response_sender = self.parse_packet(response)
                                
                                if response_header == "ACK" and response_str == "PIN CHECK":
                                    # ready to send PIN to server
                                    self.socket.sendall(self.make_packet("DATA", arduino_input))
                                    
                                    pin_check = self.socket.recv(4096)
                                    
                                    if pin_check:
                                        pin_check_header, pin_check_str, pin_check_sender = self.parse_packet(pin_check)
                                        

                                        if pin_check_header == "DATA":
                                            if pin_check_str == "PIN CHECK FAIL":
                                                
                                                print("step off bitch, that pin wrong yo.")
                                                
                                                if self.debug == 'n':
                                                    self.arduino.write("AD" + "step off bitch")
                                            
                                            else:
                                                # PIN was good
                                                print("welcome {}.".format(pin_check_str))
                                                
                                                if self.debug == 'n':
                                                    self.arduino.write("AG" + pin_check_str)
                                                
                                                self.camera.take_picture()
                                                
                                        else:
                                            raise Exception("UNKNOWN DATA RECEIVED FROM SERVER")
                            
                                elif response_header == "ERROR":
                                    raise Exception("AN ERROR PACKET WAS RECEIVED:: {}".format(response_str))  
                                
                                else:
                                    raise Exception("UNKNOWN DATA RECEIVED FROM SERVER")                                
                                   
    
                except:
                    self.socket.sendall(self.make_packet("ERROR", self.create_log(sys.exc_info())))
                    #socket.close()
                    print(sys.exc_info())
                    
                    


                ################################### LISTEN FOR COMMAND ###################################
                try:

                    server_cmd = self.socket.recv(4096)
    
                    if server_cmd:
                        server_cmd_header, server_cmd_msg, server_id = self.parse_packet(server_cmd)
                        
                        if server_cmd_header == "CMD":

                            try:
                                server_cmd_msg, door_id = server_cmd_msg.split('&')
    
                                if server_cmd_msg == "LOCK DOOR":
                                    

                                    self.socket.sendall(self.make_packet("CMD", "LOCK DOOR&" + door_id))
    
                                    if self.debug == 'n':
                                      
                                        self.arduino.write("TUFAYL IS HOMO")
    
                                    print("DEBUG: TUFAYL IS HOMO")
    
                                elif server_cmd_msg == "UNLOCK DOOR":

                                    self.socket.sendall(self.make_packet("CMD", "UNLOCK DOOR&" + door_id))
    
                                    if self.debug == 'n':
                                        self.arduino.write("TUFAYL IS SLIGHTLY HOMO")
    
                                    print("DEBUG: TUFAYL IS SLIGHTLY HOMO")
                            
                            except:
                                pass
                            
                            
                    
                        else:
                            self.socket.sendall(self.make_packet("ERROR", "DON'T KNOW WHAT I GOT", self.ID))
                
                
                except:
                    self.socket.sendall(self.make_packet("ERROR", self.create_log(sys.exc_info()), self.ID))
                    #socket.close()
                    print(err)                        
            
            
            except KeyboardInterrupt:
                self.socket.close()
                sys.exit(0)
                
    
    """
    make an packet guy
    """
    def make_packet(self, type, data):

        return ("{}\x00{}\x00{}".format(type, data, self.ID)).encode()

    
    """
    deconstruct packet

    """
    def parse_packet(self, data):
        
        return data.decode().split('\x00') 
    
    def create_log(self, exc):
        
        return self.formatter.formatException(exc)
                

    def buzz_subroutine(self):
        
        if self.debug == 'n':
            self.arduino.write("AG")
        
        self.camera.take_picture()


    def pin_check_subroutine(self):
        pass


