# Author: Martin Klamrowski
# Last modified: 5/12/2018

import socket, time, sys, logging
from components.devices import Camera, Arduino
from components import config


class DoorLock:
    """
    This class models the behaviour of a door lock (client for the You Safe Bolt 
    system. The communication protocol is described in the README.
    
    To run the door lock call run() on it.
    """    
    
    def __init__(self, ID, debug, testing):
        """
        Constructor.
        
        DoorLock.__init__(identifier, debug, testing) --> DoorLock
        """
        self.ID = ID
        
        # device setup
        self.camera = Camera()
        self.debug = debug
        self.testing = testing
        self.formatter = logging.Formatter("\%(asctime)s \%(levelname)s \%(identifier)s \%(message)s\n")        
        
        # is Arduino connected to serial port?
        if self.debug == 'n':
            self.arduino = Arduino()       
        
        # connect to server
        self.init_conn()
       
    
    
    def init_conn(self):
        """
        Setup ApplicationServer connection. Quit if password fail.
        
        DoorLock.init_conn() --> None
        """
        
        SERVER_ADDRESS = '192.168.0.21'
        PORT = 8018
        SERVER_PASSWORD = "biratkingofcomedy"        
        connected = False
        
        # check if test module is being run
        if self.testing == 'n':            
            while not connected:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                try:
                    self.socket.connect((SERVER_ADDRESS, PORT))
                    
                    # server verification
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
    
    
    
    def run(self):
        """    
        Main loop. Call this function on a DoorLock object to run it. Ctrl-C to shutdown.
        
        DoorLock.run() --> None
        """
        running = True
        while running:
            ################################### ARDUINO POLLING ###################################
            try:
                print("DEBUG: running")
                if self.debug == 'n':
                    # Arduino is connected
                    inp = self.arduino.read()
                                   
                else:                    
                    inp = str(input("Enter Packet, Enter Key to skip. Ex: (DATA&BUZZ)\n"))                

                if inp:
                    self.socket.setblocking(True)
                    arduino_input_header, arduino_input = inp.split('&')
                
                    if arduino_input_header == "DATA":            
                        if arduino_input == "BUZZ":
                            # buzz the owner
                            self.buzz_subroutine()
                            continue                        
                        
                        else:
                            # a PIN was sent by the Arduino
                            self.pin_check_subroutine(arduino_input)
                            continue
                            
                
                ########################## LISTEN FOR COMMAND FROM SERVER #########################
                else:
                    self.socket.settimeout(1)                    
                    
                    # check if a command was received
                    try:
                        cmd = self.socket.recv(4096)

                    except:
                        print("DEBUG: receive timed out")
                        continue

                    else:                        
                        cmd_hdr, cmd_msg, cmd_sdr = self.parse_packet(cmd)
                        
                        if cmd_hdr == "CMD":
                            if cmd_msg == "LOCK DOOR":                 
                                # a remote lock was issued
                                
                                if self.debug == 'n':
                                    # tell Arduino to lock the door
                                    self.arduino.write("LD")

                                print("DEBUG: locking override finished")

                            elif cmd_msg == "UNLOCK DOOR":
                                # a remote unlock was issued
                                
                                if self.debug == 'n':
                                    # tell Arduino to unlock the door
                                    self.arduino.write("UD")

                                print("DEBUG: unlocking override finished")                      
            
            except (KeyboardInterrupt, SystemExit):
                self.socket.sendall(self.make_packet("CMD", "SHUTTING DOWN"))
                raise    
            
            except Exception as e:
                self.socket.sendall(self.create_log(sys.exc_info()))
    
    
    
    def buzz_subroutine(self):
        """
        Subroutine to handle buzzer. A picture is taken and sent to the ApplicationServer.
    
        DoorLock.buzz_subroutine() --> None
        """
        self.socket.sendall(self.make_packet("CMD", "BUZZ"))
        
        response = self.socket.recv(4096)

        if response:
            response_hdr, response_msg, response_sdr = self.parse_packet(response)
                                
            if response_hdr == "ACK" and response_msg == "BUZZ":
                # ready to send picture to server
                pic_num = self.camera.take_picture()
                pic_file = open("{}.png".format(pic_num), 'rb')

                # if camera is broken uncomment line below
                #pic_file = open("1.png", 'rb')
                
                pic_bytes = pic_file.read(1024)
                
                # Pi 1 is slow so need a loop
                while pic_bytes:                    
                    self.socket.send(pic_bytes)
                    pic_bytes = pic_file.read(1024)
                    
                pic_file.close()
                
                confirm = self.socket.recv(4096)

                if confirm:
                    confirm_hdr, confirm_msg, confirm_sdr = self.parse_packet(confirm)
                    if confirm_hdr == "DATA" and confirm_msg == "PICTURE RECEIVED":
                        print("DEBUG: confirmed receive")
                    
                    

    def pin_check_subroutine(self, pin):
        """
        Subroutine to handle pin check.
    
        DoorLock.pin_check_subroutine(pin) --> None
        """
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

                    if pin_check_header == "DATA":
                        if pin_check_str == "PIN CHECK FAIL":
                            
                            print("DEBUG: incorrect PIN")
                            
                            if self.debug == 'n':
                                # tell Arduino access is denied
                                self.arduino.write("AD")
                        
                        else:
                            # PIN was good
                            print("DEBUG: correct PIN")

                            if self.debug == 'n':
                                # tell Arduino access is granted
                                self.arduino.write("AG" + pin_check_str)
                            

##################################################
    # UTILITY FUNCTIONS
##################################################
    
    def make_packet(self, type, data):
        """
        Returns a bytes packet in the form of "HEADER\\x00MSG\\x00SENDER".
        
        ApplicationServer.make_packet(header, msg) --> bytes
        """        
        return ("{}\x00{}\x00{}".format(type, data, self.ID)).encode()
    
    
    
    def parse_packet(self, data):
        """
        Deconstructs a bytes packet.
        
        ApplicationServer.parse_packet(packet) --> list
        """
        return data.decode().split('\x00') 


    
    def create_log(self, exc):
        """
        Create log data to send to server
        
        DoorLock.create_log(error) --> str
        """
        return self.formatter.formatException(exc)     
