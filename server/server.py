import socket, select, time, sqlite3, logging, sys, threading

class ApplicationServer():
    
    def __init__(self):
        
        self.ID = 'S'
        self.num_pics = 0
        self.pics_on_file = []
        self.mobile_socket = None

        self.init_log()
        self.init_db()        
        
        # server setup
        ADDRESS = '192.168.0.21'
        PORT = 2018        
        
        self.client_sockets = []
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
            print("DEBUG: " + curr.fetchall())
        
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
            
            try:
                threading.Thread(target=self.client_thread, args=(client_socket, client_address)).start()

            except:
                self.log_it(sys.exc_info())

        self.server_socket.close()





    def client_thread(self, socket, address):
        print("DEBUG: connected to {}:{}".format(address[0], address[1]))
        connected = True

        while connected:
            msg = socket.recv(4096)                        
            print("DEBUG: ".format(msg))
            
            if msg:                            
                msg_header, msg_str, msg_sender = self.parse_packet(msg)
                
                if msg_header == "CMD":                        
                    if msg_str == "PIN CHECK":
                        # get ready to receive pin
                        
                        socket.sendall(self.make_packet("ACK", "PIN CHECK"))
                            
                        
                        pin = socket.recv(4096)
                        
                        if pin:
                            pin_header, pin_str, pin_sender = self.parse_packet(pin)
                            
                            if pin_header == "DATA":                                                
                                name = self.search_db(int(pin_str))
                            
                                if name:
                                    socket.sendall(self.make_packet("DATA", name))
                                
                                else:
                                    socket.sendall(self.make_packet("DATA", "PIN CHECK FAIL"))                                    
                    
                    
                    
                    elif msg_str == "BUZZ":
                        
                        socket.sendall(self.make_packet("ACK", "BUZZ"))
                        pic = socket.recv(1024)
                        self.num_pics += 1
                        pic_file = open("{}.png".format(self.num_pics), 'wb')
                        
                        while pic:

                            pic_file.write(bytes(pic))
                            pic = socket.recv(1024)
                            

                        socket.sendall(self.make_packet("DATA", "RECEIVED"))

                        self.pics_on_file.append(self.num_pics)
                        pic_file.close()
                        
                    elif msg_str == "SHUTTING DOWN":
                        socket.close()
                        connected = False
                        
                    """   
                    try:
                        msg_str, door_number = msg_str.split('&')

                        if msg_str == "LOCK DOOR":
                            # get ready to lock door

                            print(self.num_pics)
                            socket.sendall(self.make_packet("ACK", "LOCK DOOR"))
                            file = open("{}.png".format(self.num_pics), 'rb')

                            file_bytes = file.read()
                            
                            socket.sendall(file_bytes)

                            file.close()
                            
                            
                        
                            print("BIRAT LOCK")
                    
                        elif msg_str == "UNLOCK DOOR":
                            # get ready to unlock door

                            socket.sendall(self.make_packet("ACK", "UNLOCK DOOR"))

                            print("BIRAT UNLOCK")

                    except Exception as e:
                        pass
                    """







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

    

    
        
