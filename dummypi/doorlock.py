# Author: Angie Byun

import socket, time, serial, sys, logging
from components.camera import Camera
from components.arduino import Arduino


"""
Dummypi DoorLock Class (RPi2)
"""
class DoorLock:
    
    def __init__(self, ID, debug, testing):

        # Device Setup
        self.camera = Camera()
        self.debug = debug
        self.testing = testing
        self.formatter = logging.Formatter("\%(asctime)s \%(levelname)s \%(identifier)s \%(message)s\n")
        self.ID = ID
        
        # Arduino Debug
        if self.debug == 'n':
            self.arduino = Arduino()       
        
        # Connect to Server
        self.init_conn()
       
    """
    Init Server Connection
    """
    def init_conn(self):
        SERVER_ADDRESS = '192.168.0.21'
        PORT = 8018
        SERVER_PASSWORD = "biratkingofcomedy"        
        connected = False
        
        if self.testing == 'n':

            while not connected:
                # TCP socket connection 
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                try:
                    self.socket.connect((SERVER_ADDRESS, PORT))
                    
                    # Verifies server
                    self.socket.sendall(self.make_packet("DATA", SERVER_PASSWORD))
                    
                    response = self.socket.recv(4096)
                    
                    if response:
                        response_hdr, response_msg, response_sdr = self.parse_packet(response)
                        
                        if response_hdr == "ERROR" and response_msg == "IDENTIFY FAILED":
                            raise Exception("PASSWORD FAIL")
                        
                        elif response_hdr == "DATA" and response_msg == "CONNECTED":
                            connected = True
                    
                    else:
                        raise Exception("CONNECTION FAIL")
                    
                
                except Exception as e:
                    if e == "PASSWORD FAIL":
                        print("DEBUG: server connection failed (invalid credentials)")
                        print("DEBUG: quitting")
                        break
                    
                    else:
                        print(e)
                        print("DEBUG: server connection failed (could not connect), trying again in 10s")
                        time.sleep(10)
                              
        else:
            print("DEBUG: socket setup skipped")
    
    
    
    """
    Main Loop
    """
    def run(self):
        
        while True:

            ##### Arduino #####

            try:
                # Enter pin 
                print("DEBUG: RUNNING")
                print("DEBUG: Please enter pin: ")

                # input to simulate Arduino 
                if self.debug == 'n':
                    inp = self.arduino.read()
                    print(inp)
                    print(len(inp[0]))

                if len(inp[0]):
                    print("in")
                    self.socket.setblocking(True)
                    arduino_input_header, arduino_input = inp[0], inp[1]

                    # the header of the input is DATA
                    if arduino_input_header == "DATA":
                                
                        # if the header is DATA and MSG is BUZZ, go through buzz subroutin
                        if arduino_input == "BUZZ":
                            # $ buzz the owner
                            self.buzzSubroutine()
                            continue
                        
                        else:
                            # four digit number is entered (passcode) then go through pin check subroutine
                            self.pinCheckSubroutine(arduino_input)
                            continue
                            
                
                ##### Listen for command from server #####

                # wait for 1 second to receive 
                else:
                    self.socket.settimeout(1)
                    
                    # check if command was received
                    try:
                        cmd = self.socket.recv(4096)
                        print(cmd)

                    except socket.timeout:
                        continue


                    else:                        
                        cmd_hdr, cmd_msg, cmd_sdr = self.parse_packet(cmd)

                        # if door is locked from the remote, lock door and print "Door Locked"
                        if cmd_hdr == "CMD":

                            if cmd_msg == "LOCK DOOR":                 

                                if self.debug == 'n':                              
                                    self.arduino.write("Door Locked")
                            # if door is unlocked from the remote, door is unlocked and "Door Unlocked" is printed
                            elif cmd_msg == "UNLOCK DOOR":

                                if self.debug == 'n':
                                    self.arduino.write("Door Unlocked")

                      
            
            except (KeyboardInterrupt, SystemExit):
                self.socket.sendall(self.make_packet("CMD", "SHUTTING DOWN"))
                raise    
            
            except Exception as e:
                print(e)
                break
    
    """
    Buzzer Subroutine.

    """
    def buzzSubroutine(self):

        # preloaded picture is sent to the server
        pic_num = self.camera.takePicture()

        print("PIC {}".format(pic_num))       
        
        self.socket.sendall(self.make_packet("CMD", "BUZZ"))
        
        response = self.socket.recv(4096)

        if response:
            response_hdr, response_msg, response_sdr = self.parse_packet(response)
                                
            if response_hdr == "ACK" and response_msg == "BUZZ":

                pic_file = open("{}.png".format(pic_num), 'rb')
                pic_bytes = pic_file.read(1024)

                while pic_bytes:
                    
                    self.socket.send(pic_bytes)
                    pic_bytes = pic_file.read(1024)

                
                pic_file.close()
                
                confirm = self.socket.recv(4096)

                # confirmation message when picture is received at the server end.
                if confirm:
                    confirm_hdr, confirm_msg, confirm_sdr = self.parse_packet(confirm)
                    if confirm_hdr == "DATA" and confirm_msg == "PICTURE RECEIVED":
                        print("DEBUG: confirmed receive")
                    
                    

    """
    Pin Check Subroutine to handle pin check.

    """
    def pinCheckSubroutine(self, pin):
        self.socket.sendall(self.make_packet("CMD", "PIN CHECK"))
                        
        response = self.socket.recv(4096)
        
        if response:
            response_hdr, response_msg, response_sdr = self.parse_packet(response)
            
            if response_hdr == "ACK" and response_msg == "PIN CHECK":

                # ready to send PIN to server
                self.socket.sendall(self.make_packet("DATA", pin))
                
                pin_check = self.socket.recv(4096)
                
                if pin_check:
                    pin_check_header, pin_check_str, pin_check_sender = self.parse_packet(pin_check)
                    
                    # Wrong pin was entered and access denied message is printed.
                    if pin_check_header == "DATA":
                        if pin_check_str == "PIN CHECK FAIL":
                            
                            print("DEBUG: wrong pin, go away.")

                            # Take a picture and send it to server
                            pic_num = self.camera.takePicture()
                        
                        else:
                            # Correct pin was entered and access was granted.

                            if self.debug == 'n':
                                self.arduino.write("AG" + pin_check_str)
                            
                            


   ##### Utility Functions #####


    """
    Make packet.
    """
    def make_packet(self, type, data):

        return ("{}\x00{}\x00{}".format(type, data, self.ID)).encode()

    
    """
    Deconstruct packet.

    """
    def parse_packet(self, data):
        
        return data.decode().split('\x00') 


    """
    Create log to send to server.
    """
    def create_log(self, exc):
        
        return self.formatter.formatException(exc)     
