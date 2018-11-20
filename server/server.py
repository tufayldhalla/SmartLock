import socket, select, time, sqlite3, logging, sys

class ApplicationServer():
    
    def __init__(self):
        
        self.ID = 'S'

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
        
        self.conn = sqlite3.connect("server.db")
        self.curr = self.conn.cursor()
        
        try:
            # note: Access_Level ranked low to high; 1 to 3            
            self.curr.execute('CREATE TABLE Users (Name TEXT, Pass INTEGER, Date_Added TEXT, Access_Level INTEGER, PRIMARY KEY (Pass))')
        
        except sqlite3.OperationalError:
            d = {'identifier': '{}'.format(self.ID)}
            self.log.error(self.formatter.formatException(sys.exc_info()), extra=d)
        
        # $ FOR TESTING 1 ENTRY HAS BEEN ADDED
        self.curr.execute('INSERT INTO Users VALUES("bigdaddy6969", 8008, "09-11-2018", 3)')
    
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
        self.client_sockets.append(self.server_socket)
        
        print("DEBUG: running")
        while True:
        
            rsockets, wsockets, esockets = select.select(self.client_sockets, [], [], 0)
        
            for socket in rsockets:        
                if socket == self.server_socket:
                    print(1) 
                    client_socket, client_address = self.server_socket.accept()
                    print(client_address)
                    self.client_sockets.append(client_socket)                   
                    
                else:                    
                    try:
                        print(2)
                        msg = socket.recv(4096)                        
                        print(msg)
                        print(msg.decode())
                        
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
                                
                                try:
                                    msg_str, door_number = msg_str.split('&')

                                    if msg_str == "LOCK DOOR":
                                        # get ready to lock door
                                    
                                        socket.sendall(self.make_packet("ACK", "LOCK DOOR"))
                                    
                                        print("BIRAT LOCK")
                                
                                    elif msg_str == "UNLOCK DOOR":
                                        # get ready to unlcok door

                                        socket.sendall(self.make_packet("ACK", "UNLOCK DOOR"))

                                        print("BIRAT UNLOCK")

                                except Exception as e:
                                    print(e)
                                    

                            
                            elif msg_header == "ERROR":
                                d = {'identifier': '{}'.format(msg_sender)}
                                self.log.error(msg_str, extra=d)
                                pass
                                
                            else:
                                print("GOT THIS")
                                socket.sendall(self.make_packet("ERROR", "INVALID PROTOCOL"))
                        
                    
                    except Exception as e:
                        print(3)
                        print(e)
                        d = {'identifier': '{}'.format(self.ID)}
                        self.log.error(self.formatter.formatException(sys.exc_info()), extra=d)
                        continue

                    finally:
                        print(4)
                        socket.close()
                        self.client_sockets.remove(socket)
        
        self.server_socket.close()                
    
    """
    search database for specified query, currently only searches for PIN
    """
    def search_db(self, query):
        
        self.curr.execute('SELECT Name FROM Users WHERE Pass = "{}" '.format(query))
        
        # $ will later change to iterate over the cursor
        fetch = str(self.curr.fetchall())
        
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
        
