import socket, time, sqlite3, logging, sys, threading, queue

class ApplicationServer():
    
    def __init__(self):
        
        self.ID = 'S'
        self.identify_password = "biratkingofcomedy"
        self.num_pics = 0
        self.pics_on_file = []

        self.cmd_list = []
        self.client_sockets = []
        self.client_addresses = []
        self.app_address = ""               

        self.init_log()
        self.init_db()        
        
        # server setup
        ADDRESS = '192.168.0.21'
        PORT = 8018        
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((ADDRESS, PORT))
        self.server_socket.listen(10)

    
    """
    init database
    """
    def init_db(self):
        
        conn = sqlite3.connect("server.db")
        curr = conn.cursor()
        
        try:
            # note: Access_Level ranked low to high; 1 to 3            
            curr.execute('CREATE TABLE Users (Name TEXT, Pass INTEGER, Date_Added TEXT, Access_Level INTEGER, PRIMARY KEY (Pass))')
            
            # $ FOR TESTING ENTRIES HAVE BEEN ADDED
            curr.execute('INSERT INTO Users VALUES("bigdaddy6969", 8008, "09-11-2018", 3)')
            curr.execute('INSERT INTO Users VALUES("cheesewick", 1234, "28-11-2018", 1)')
            curr.execute('SELECT * FROM Users')
            print("DEBUG: " + str(curr.fetchall()))
        
        except sqlite3.OperationalError:
            self.log_it(sys.exc_info())        

        conn.commit()
        conn.close()
        
    
    """
    init logging
    """
    def init_log(self):
        
        logging.basicConfig( filename = "server.log",
                             level = logging.DEBUG,
                             format = "\%(asctime)s \%(levelname)s \%(identifier)s \%(message)s\n"
                             )        
        self.log = logging.getLogger()       
        self.formatter = logging.Formatter("\%(asctime)s \%(levelname)s \%(identifier)s \%(message)s\n")
                    


    """
    main loop
    """
    def run(self):

        print("DEBUG: running")
        print("DEBUG: server is listening")
        
        running = True

        while running:

            client_socket, client_address = self.server_socket.accept()
            print("A")     
            
            try:
                identify = client_socket.recv(4096)
                print("B")

                if identify:
                    print(identify)
                    identify_hdr, identify_msg, identify_sdr = self.parse_packet(identify)
                    print("C")
                    # super high-level security
                    if identify_hdr == "DATA" and identify_msg == self.identify_password and self.client_type(identify_sdr):        
                        print("D")
                        try:
                            identifier_type = self.client_type(identify_sdr)
                            
                            # if its a doorlock
                            if identifier_type == "D":
                                print("EA")
                                threading.Thread(target=self.client_thread, args=(client_socket, client_address, identify_sdr)).start()
                                self.client_sockets.append(client_socket)
                                self.client_addresses.append(client_address[0])

                            """
                            # if its the app
                            elif identifier_type == "M":
                                print("EB")
                                #threading.Thread(target=self.app_thread, args=(client_socket, client_address, identify_sdr)).start()
                                
                                self.app_address = client_address[0]
                                self.client_addresses.append(client_address[0])
                                print("DEBUG: connected to app at {}:{}".format(client_address[0], client_address[1]))
                            """
                            
                        except:
                            self.log_it(sys.exc_info())
                            print("DEBUG: could not create thread")
                            
                    # have to handle app here cause the app developer is an autist
                    elif identify_sdr == "M":
                        self.app_address = client_address[0]
                        recv_hdr, recv_msg, recv_sdr = identify_hdr, identify_msg, identify_sdr
                        if recv_hdr == "CMD":
                
                            if recv_msg.startswith("LOCK DOOR"):   
                                # $ get ready to lock door
                                
                                recv_msg, door_number = recv_msg.split('&')                        
                                client_socket.sendall(self.make_packet("ACK", "LOCK DOOR&" + door_number))
                                
                                
                                #add to queue?
                                
                                self.add_command(("D{}".format(door_number), self.make_packet("CMD", "LOCK DOOR")))
                                
                                print("DEBUG: finished lock")
                        
                            
                            elif recv_msg.startswith("UNLOCK DOOR"):
                                # $ get ready to unlock door
                                
                                recv_msg, door_number = recv_msg.split('&')
                                client_socket.sendall(self.make_packet("ACK", "UNLOCK DOOR&" + door_number))
                                
                                
                                #add to queue?
                                
                                self.add_command(("D{}".format(door_number), self.make_packet("CMD", "UNLOCK DOOR")))
                                
                                print("DEBUG: finished unlock")
                                
                            elif recv_msg.startswith("ADD USER"):
                                # $ adding user
                                
                                recv_msg, user_data = recv_msg.split('&')                        
                                client_socket.sendall(self.make_packet("ACK", "ADD USER"))

                            
                            elif recv_msg == "SHUTTING DOWN":
                                self.app_address = ""
                                self.client_addresses.remove(client_address[0])
                                client_socket.close()
                                connected = False

                    else:
                        client_socket.sendall(self.make_packet("ERROR", "IDENTIFY FAILED"))
                        
                
            except:
                print("DEBUG: could not talk with client")

            
            
        self.server_socket.close()

        
        
        
        
    """
    thread method to handle client
    """
    def client_thread(self, socket, address, ID):
        print("DEBUG: connected to doorlock at {}:{}".format(address[0], address[1]))
        connected = True
        
        socket.sendall(self.make_packet("DATA", "CONNECTED"))

        socket.setblocking(False)
        
        while connected:

            if self.cmd_list:
                print(1)
                for cmd in self.cmd_list:
                    print(2)
                    if ID in cmd:
                        socket.sendall(cmd[1])
                        self.cmd_list.remove(cmd)
                        print(3)
                        break
            try:
                recv = socket.recv(4096)                        
                print("DEBUG: {}".format(recv))

            except:
                continue
                    
            else:
                if recv:                            
                    recv_hdr, recv_msg, recv_sdr = self.parse_packet(recv)

                    socket.setblocking(True)
                    
                    if recv_hdr == "CMD":                        
                        if recv_msg == "PIN CHECK":
                            # get ready to receive pin
                            
                            socket.sendall(self.make_packet("ACK", "PIN CHECK"))                            
                            
                            pin = socket.recv(4096)
                            
                            if pin:
                                pin_hdr, pin_msg, pin_sdr = self.parse_packet(pin)
                                
                                if pin_hdr == "DATA":                                                
                                    name = self.search_db(int(pin_msg))
                                
                                    if name:
                                        socket.sendall(self.make_packet("DATA", name))
                                    
                                    else:
                                        socket.sendall(self.make_packet("DATA", "PIN CHECK FAIL"))                 
                        
                        
                        elif recv_msg == "BUZZ":
                            """
                            send a notification + picture to the owner's phone
                             - the picture is received from the respective doorlock client
                            """
                            
                            socket.sendall(self.make_packet("ACK", "BUZZ"))
                            
                            # prepare to receive picture
                            pic = socket.recv(1024)
                            self.num_pics += 1
                            pic_file = open("{}.png".format(self.num_pics), 'wb')
                            
                            # its slow af so need a loop
                            while pic:

                                pic_file.write(bytes(pic))
                                pic = socket.recv(1024)                            

                            socket.sendall(self.make_packet("DATA", "PICTURE RECEIVED"))

                            self.pics_on_file.append("{}.png".format(self.num_pics))
                            pic_file.close()
                            
                        
                        elif recv_msg == "SHUTTING DOWN":
                            self.client_sockets.remove(socket)
                            self.client_addresses.remove(address[0])
                            socket.close()                        
                            print("DEBUG: shutting down")
                            connected = False




            


    """
    UTILITY FUNCTIONS
    """
    
    """
    search database for specified query, currently only searches for PIN
    """
    def search_db(self, query):

        conn = sqlite3.connect("server.db")
        curr = conn.cursor()

        #curr.execute('SELECT * FROM Users')
        
        curr.execute('SELECT Name FROM Users WHERE Pass = "{}" '.format(query))
        
        # $ will later change to iterate over the cursor
        fetch = str(curr.fetchall())
        print("DEBUG: fetched -> " + fetch)
        
        fetch = fetch.replace("(", "")
        fetch = fetch.replace(")", "")
        fetch = fetch.replace(",", "")
        fetch = fetch.replace("'", "")
        fetch = fetch.replace("[", "")
        fetch = fetch.replace("]", "")
        #print(fetch)
        return fetch
    
    
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
    log an error
    """
    def log_it(self, error_info):
        d = {'identifier': '{}'.format(self.ID)}
        self.log.error(self.formatter.formatException(error_info), extra=d)
        
        
    """
    determine client type from given identifier
    """
    def client_type(self, identifier):
        
        # doorlock
        if identifier.startswith("D"):
            return "D"
        
        # mobile app
        elif identifier.startswith("M"):
            return "M"
        
        # not a valid id
        else:
            return ""


    """
    method to handle adding to command list
    """
    def add_command(self, cmd):

        print("L1", self.cmd_list)
        for c in self.cmd_list:
            
            if cmd[0] in c:
                print(cmd)
                print(c)
                
                self.cmd_list.remove(c)
                self.cmd_list.append(cmd)
                print("L2", self.cmd_list)
                return
            
        self.cmd_list.append(cmd)
        print("L3", self.cmd_list)





    """
    DELETED FUNCTIONS
    """

    """
    thread method to handle app
    """
    def app_thread(self, socket, address, ID):
        print("DEBUG: connected to app at {}:{}".format(address[0], address[1]))
        connected = True
        
        #socket.sendall(self.make_packet("DATA", "CONNECTED"))

        while connected:
            recv = socket.recv(4096)                        
            print("DEBUG: {}".format(recv))

            if recv:                            
                recv_hdr, recv_msg, recv_sdr = self.parse_packet(recv)
                
                if recv_hdr == "CMD":
            
                    if recv_msg.startswith("LOCK DOOR"):   
                        # $ get ready to lock door
                        
                        recv_msg, door_number = recv_msg.split('&')                        
                        socket.sendall(self.make_packet("ACK", "LOCK DOOR&" + door_number))
                        
                        """
                        add to queue?
                        """
                        #self.cmd_queue.put(self.)
                        
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

    
            
        
