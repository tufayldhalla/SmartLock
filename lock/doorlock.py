import socket, time, serial, sys, logging
from components.camera import Camera
from components.devices import Arduino
from components import config

"""
DoorLock Class (RPi3)
"""
class DoorLock:
    
    def __init__(self, ID, debug, testing):
        

        # device setup
        self.camera = Camera()
        self.debug = debug
        self.testing = testing
        self.formatter = logging.Formatter("\%(asctime)s \%(levelname)s \%(identifier)s \%(message)s\n")
        self.ID = ID
        
        # is arduino connected to serial port?
        if self.debug == 'n':
            self.arduino = Arduino()       
        
        # connect to server
        self.init_conn()
       
    """
    init server connection
    """
    def init_conn(self):
        SERVER_ADDRESS = '192.168.0.21'
        PORT = 8018
        SERVER_PASSWORD = "biratkingofcomedy"        
        connected = False
        
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
    
    
    
    
    
    
    
    
    
    """
    main loop
    """
    def run(self):
        
        while True:

            ################################### ARDUINO ###################################

            try:
                print("DEBUG: running")
                print("DEBUG: enter pin my guy")
                if self.debug == 'n':
                    inp = self.arduino.read()
                    print(inp)
                    print(len(inp))

                                   
                else:                    
                    inp = str(input("Enter Packet (DATA&BUZZ)"))
                    print(inp)
                    print(len(inp))
                

                if inp:
                    self.socket.setblocking(True)
                    arduino_input_header, arduino_input = inp.split('&')
                
                    if arduino_input_header == "DATA":
                        if arduino_input == "WAKE":
                            # $ wake the reader (not implemented yet)
                            self.arduino.write("UD")
                            continue
                                
                    
                        elif arduino_input == "BUZZ":
                            # $ buzz the owner
                            self.buzz_subroutine()
                            continue
                        
                        elif arduino_input == "FINGER":
                            # $ fingerprint access
                            continue
                        
                        else:
                            # a PIN was sent by the Arduino
                            self.pin_check_subroutine(arduino_input)
                            continue
                            
                
                ################################### LISTEN FOR COMMAND FROM SERVER ###################################

                else:
                    self.socket.settimeout(1)
                    ###INCOMPLETE

                    #self.socket.setblocking(False)
                    
                    try:
                        cmd = self.socket.recv(4096)
                        print(cmd)

                    except socket.timeout:
                        continue

                    else:                        
                        cmd_hdr, cmd_msg, cmd_sdr = self.parse_packet(cmd)
                        
                        if cmd_hdr == "CMD":

                            if cmd_msg == "LOCK DOOR":                 

                                if self.debug == 'n':                              
                                    self.arduino.write("LD")

                                print("DEBUG: locking override finished")

                            elif cmd_msg == "UNLOCK DOOR":

                                if self.debug == 'n':
                                    self.arduino.write("UD")

                                print("DEBUG: unlocking override finished")
                      
            
            except (KeyboardInterrupt, SystemExit):
                self.socket.sendall(self.make_packet("CMD", "SHUTTING DOWN"))
                raise    
            
            except Exception as e:
                print(e)
                break
    
    """
    subroutine to handle buzzer

    ###INCOMPLETE
    """
    def buzz_subroutine(self):
        
        #if self.debug == 'n':
         #   self.arduino.write("AG")
        pic_num = self.camera.take_picture()

        print("PIC {}".format(pic_num))       
        
        self.socket.sendall(self.make_packet("CMD", "BUZZ"))
        
        response = self.socket.recv(4096)

        if response:
            response_hdr, response_msg, response_sdr = self.parse_packet(response)
                                
            if response_hdr == "ACK" and response_msg == "BUZZ":
                # ready to send picture to server

                pic_file = open("{}.png".format(pic_num), 'rb')
                pic_bytes = pic_file.read(1024)

                while pic_bytes:
                    
                    self.socket.send(pic_bytes)
                    pic_bytes = pic_file.read(1024)

                
                pic_file.close()
                
                confirm = self.socket.recv(4096)

                if confirm:
                    confirm_hdr, confirm_msg, confirm_sdr = self.parse_packet(confirm)
                    if confirm_hdr == "DATA" and confirm_msg == "PICTURE RECEIVED":
                        print("DEBUG: confirmed receive")
                    
                    

    """
    subroutine to handle pin check

    ###INCOMPLETE
    """
    def pin_check_subroutine(self, pin):
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
                            
                            print("DEBUG: step off bitch, that pin wrong yo.")
                            
                            if self.debug == 'n':
                                self.arduino.write("AD" + "step off bitch")

                            pic_num = self.camera.take_picture()
                        
                        else:
                            # PIN was good
                            print("welcome {}.".format(pin_check_str))

                            if self.debug == 'n':
                                self.arduino.write("AG" + pin_check_str)
                            
                            
                      





















    """
    UTILITY FUNCTIONS
    """

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


    """
    create log to send to server
    """
    def create_log(self, exc):
        
        return self.formatter.formatException(exc)     
