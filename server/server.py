# Author: Martin Klamrowski
# Last modified: 5/12/2018

import socket, time, sqlite3, logging, sys, threading, datetime


class ApplicationServer():
    """
    This class models the behaviour of the server for the You Safe Bolt system. The
    communication protocol is described in the README.
    
    To run the server call run() on it.
    """    
    
    def __init__(self):
        """
        Constructor.
        
        ApplicationServer.__init__() --> ApplicationServer
        """
        self.ID = 'S'
        self.num_pics = 0
        self.pics_on_file = []
        
        # a client must provide this password to communicate with the server
        self.identify_password = "biratkingofcomedy"        

        self.cmd_list = []
        self.client_sockets = []
        self.client_addresses = []
        
        # a static ip was set on the phone
        self.app_address = '192.168.0.250'
        self.app_port = 2001
        
        # initialize
        self.init_log()
        self.init_db()        
        
        # server setup
        ADDRESS = '192.168.0.21'
        PORT = 8018        
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ADDRESS, PORT))
        self.server_socket.listen(10)

    
    
    def init_db(self):
        """
        Initializes the database for the ApplicationServer.
         - A .db file is created and formatted
         
        ApplicationServer.init_db() --> None
        """
        conn = sqlite3.connect("server.db")
        curr = conn.cursor()
        
        try:
            # note: Access_Level ranked low to high; 1 to 3            
            curr.execute('CREATE TABLE Users (Name TEXT, Pass INTEGER, Date_Added TEXT, Access_Level INTEGER, PRIMARY KEY (Pass))')
            
        except sqlite3.OperationalError:
            self.log_it(sys.exc_info(), self.ID)        

        conn.commit()
        conn.close()
        
    
    
    def init_log(self):
        """
        Initializes logging for the ApplicationServer.
         - A log file is opened/created
         - Creates a Logger object
         
        ApplicationServer.init_log() --> None
        """
        logging.basicConfig( filename = "server.log",
                             level = logging.DEBUG,
                             format = "\%(asctime)s \%(levelname)s \%(identifier)s \%(message)s\n"
                             )        
        self.log = logging.getLogger()       
        self.formatter = logging.Formatter("\%(asctime)s \%(levelname)s \%(identifier)s \%(message)s\n")                    


    
    def run(self):
        """
        Main system loop.
         - DoorLock clients are handled in a new thread
         - New client connections and the app are handled in the main thread
         
        ApplicationServer.run() --> None
        """
        print("DEBUG: running")
        print("DEBUG: server is listening")
        
        running = True
        while running:
            
            # listen for new connections
            client_socket, client_address = self.server_socket.accept()  
            
            try:
                identify = client_socket.recv(4096)

                if identify:
                    identify_hdr, identify_msg, identify_sdr = self.parse_packet(identify)
                    identifier_type = self.client_type(identify_sdr)
                    
                    # super high-level security
                    if identify_hdr == "DATA" and identify_msg == self.identify_password and self.client_type(identify_sdr):        
                        try:                       
                            # if its a doorlock
                            if identifier_type == "D":
                                threading.Thread(target=self.client_thread, args=(client_socket, client_address, identify_sdr)).start()
                                self.client_sockets.append(client_socket)
                                self.client_addresses.append(client_address[0])
                            
                        except:
                            self.log_it(sys.exc_info(), self.ID)
                            print("DEBUG: could not create thread")
                            

                    elif identify_sdr == "M":
                        """
                        Handling of the mobile app is done here. The app was unable to send an identify so that isn't checked.
                        """
                        print("DEBUG: connected to app at {}:{}".format(client_address[0], client_address[1]))
                        
                        self.app_address = client_address[0]
                        recv_hdr, recv_msg, recv_sdr = identify_hdr, identify_msg, identify_sdr
                        
                        # command
                        if recv_hdr == "CMD":                
                            if recv_msg.startswith("LOCK DOOR"):   
                                # get ready to lock door
                                
                                recv_msg, door_number = recv_msg.split('&')                        
                                client_socket.sendall(self.make_packet("ACK", "LOCK DOOR&" + door_number))
                                
                                # add command to client command list
                                self.add_command(("D{}".format(door_number), self.make_packet("CMD", "LOCK DOOR")))
                                
                                print("DEBUG: finished lock")
                        
                            
                            elif recv_msg.startswith("UNLOCK DOOR"):
                                # get ready to unlock door
                                
                                recv_msg, door_number = recv_msg.split('&')
                                client_socket.sendall(self.make_packet("ACK", "UNLOCK DOOR&" + door_number))
                                
                                # add command to client command list
                                self.add_command(("D{}".format(door_number), self.make_packet("CMD", "UNLOCK DOOR")))
                                
                                print("DEBUG: finished unlock")
                                

                            elif recv_msg.startswith("ADD USER"):
                                # adding user to database
                                
                                recv_msg, user_data = recv_msg.split('&')
                                self.add_db(user_data)
                                

                            elif recv_msg == "SHUTTING DOWN":
                                # disconnect from app
                                
                                self.app_address = ""
                                client_socket.close()

                    else:
                        client_socket.sendall(self.make_packet("ERROR", "IDENTIFY FAILED"))                        
                
            except:
                print("DEBUG: could not talk with client")            
            
        self.server_socket.close()
        
    
    
    def client_thread(self, sock, address, ID):
        """
        Handles the DoorLock client.
        """
        print("DEBUG: connected to doorlock at {}:{}".format(address[0], address[1]))        
        sock.sendall(self.make_packet("DATA", "CONNECTED"))
        
        # set to non blocking
        sock.setblocking(False)
        
        connected = True
        while connected:
            
            # send a pending command to the DoorLock
            if self.cmd_list:
                for cmd in self.cmd_list:
                    if ID in cmd:
                        sock.sendall(cmd[1])
                        self.cmd_list.remove(cmd)
                        break

            try:
                recv = sock.recv(4096)

            except:
                print("DEBUG: receive timed out")
                    
            else:
                if recv:                            
                    recv_hdr, recv_msg, recv_sdr = self.parse_packet(recv)

                    sock.setblocking(True)                 
                    
                    # command
                    if recv_hdr == "CMD":                        
                        if recv_msg == "PIN CHECK":
                            # get ready to receive pin
                            
                            sock.sendall(self.make_packet("ACK", "PIN CHECK"))                            
                            
                            pin = sock.recv(4096)
                            
                            if pin:
                                pin_hdr, pin_msg, pin_sdr = self.parse_packet(pin)
                                
                                if pin_hdr == "DATA":                                                
                                    name = self.search_db(int(pin_msg))
                                
                                    if name:
                                        sock.sendall(self.make_packet("DATA", name))
                                    
                                    else:
                                        sock.sendall(self.make_packet("DATA", "PIN CHECK FAIL"))                 
                        
                        
                        elif recv_msg == "BUZZ":
                            """
                            ###INCOMPLETE (app was not able to receive picture)
                            Send a notification + picture to the owner's phone
                             - the picture is received from the respective doorlock client
                            """
                            
                            sock.sendall(self.make_packet("ACK", "BUZZ"))
                            
                            # prepare to receive picture from client                        
                            pic = sock.recv(1024)
                            self.num_pics += 1
                            pic_file = open("{}.png".format(self.num_pics), 'wb')
                            
                            # Pi 1 is slow so need a loop to receive picture data
                            sock.settimeout(1)

                            try:
                                while pic:                                
                                    pic_file.write(bytes(pic))
                                    pic = sock.recv(1024)
                                    
                            except:
                                print("DEBUG: picture receive ended, or timed out")
                                
                            sock.sendall(self.make_packet("DATA", "PICTURE RECEIVED"))

                            self.pics_on_file.append("{}.png".format(self.num_pics))
                            pic_file.close()

                            try:
                                # attempt to connect to mobile app
                                app_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                app_socket.connect((self.app_address, self.app_port))

                            except:
                                print("DEBUG: error, app was not available")

                            else:
                                pic_file = open("{}.png".format(self.num_pics), 'rb')
                                pic_bytes = pic_file.read()

                                try:
                                    app_socket.sendall(pic_bytes)

                                except:
                                    print("DEBUG: error sending picture")
                                    
                            sock.setblocking(True)
                        
                        
                        elif recv_msg == "SHUTTING DOWN":
                            # disconnect from client
                            
                            self.client_sockets.remove(sock)
                            self.client_addresses.remove(address[0])
                            sock.close()                        
                            print("DEBUG: shutting down")
                            connected = False
                    
                    elif recv_hdr == "ERROR":
                        self.log_it(recv_msg, ID)


##################################################
    # UTILITY FUNCTIONS
##################################################    
    
    def search_db(self, query):
        """
        Returns result (name) of database search for given PIN.
        
        ApplicationServer.search_db(pin) --> str
        """
        conn = sqlite3.connect("server.db")
        curr = conn.cursor()
        
        curr.execute('SELECT Name FROM Users WHERE Pass = "{}" '.format(query))
        
        fetch = str(curr.fetchone())
        print("DEBUG: fetched -> {}".format( fetch ))
        
        fetch = fetch.lstrip("('")
        fetch = fetch.rstrip("',)")           
        
        conn.close()
        
        return fetch if fetch != "None" else ""



    def add_db(self, data):
        """
        Adds to the database. User data is a string of the form "name pin".
        
        add_db(data) --> None
        """
        conn = sqlite3.connect("server.db")
        curr = conn.cursor()
        
        name, pin = data.split(" ")
        
        try:
            curr.execute('INSERT INTO Users VALUES("{}", {}, "{}", 1)'.format(name, pin, datetime.datetime.now()))
            
        except:
            print("DEBUG: user already existed")
            
        conn.commit()
        conn.close()
        
        
        
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


    
    def log_it(self, error_info, device):
        """
        Logs an error to the log file.
        
        ApplicationServer.log_it(error) --> None
        """
        d = {'identifier': '{}'.format(device)}
        self.log.error(self.formatter.formatException(error_info), extra=d)
        
        
    
    def client_type(self, identifier):
        """
        Determines client type from the given identifier.
        
        ApplicationServer.client_type(id) --> str
        """
        # doorlock
        if identifier.startswith("D"):
            return "D"
        
        # app
        elif identifier.startswith("M"):
            return "M"
        
        # not a valid id
        else:
            return ""


    
    def add_command(self, cmd):
        """
        Add a command packet to the command list.
        
        ApplicationServer.add_command(packet) --> None
        """        
        for c in self.cmd_list:
            
            if cmd[0] in c:
                self.cmd_list.remove(c)
                self.cmd_list.append(cmd)

                return
            
        self.cmd_list.append(cmd) 
    
    
    



##################################################
        # DELETED FUNCTIONS
##################################################
        
    """
    thread method to handle app
    """
    def app_thread(self, socket, address, ID):
        print("DEBUG: connected to app at {}:{}".format(address[0], address[1]))
        connected = True
        
        socket.sendall(self.make_packet("DATA", "CONNECTED"))

        while connected:
            recv = socket.recv(4096)                        
            print("DEBUG: ".format(recv))        
            
            if recv_msg.startswith("LOCK DOOR"):   
                # $ get ready to lock door
                
                recv_msg, door_number = recv_msg.split('&')                        
                socket.sendall(self.make_packet("ACK", "LOCK DOOR&" + door_number))
                
                """
                add to queue?
                """
                
                print("DEBUG: finished lock")
        
            
            elif recv_msg.startswith("UNLOCK DOOR"):
                # $ get ready to unlock door
                
                recv_msg, door_number = recv_msg.split('&')
                socket.sendall(self.make_packet("ACK", "UNLOCK DOOR&" + door_number))
                
                """
                add to queue?
                """                
                
                print("DEBUG: finished unlock")
                
            
            elif recv_msg == "SHUTTING DOWN":
                socket.close()
                connected = False          
    
            
        
