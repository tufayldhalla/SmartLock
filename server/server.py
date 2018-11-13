import socket, select, time, sqlite3, logging, sys

class ApplicationServer():
    
    def __init__(self):
        
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
        
        except sqlite3.OperationalError as soe:
            self.log.error(soe)
        
        # $ FOR TESTING 1 ENTRY HAS BEEN ADDED
        self.curr.execute('INSERT INTO Users VALUES("bigdaddy6969", 8008, "09-11-2018", 3)')
    
    """
    init logging
    """
    def init_log(self):
        
        logging.basicConfig( filename = "server.log",
                             level = logging.DEBUG,
                             format = "\%(asctime)s \%(levelname)s \%(name)s \%(message)s"
                             )
        self.log = logging.getLogger()       
    
    
    """
    main loop
    """
    def run(self):
        
        self.client_sockets.append(self.server_socket)
        
        while True:
            print("DEBUG: running")
        
            rsockets, wsockets, esockets = select.select(self.client_sockets, [], [])
        
            for socket in rsockets:        
                if socket == self.server_socket:
        
                    client_socket, client_address = self.server_socket.accept()
                    self.client_sockets.append(client_socket)                   
                    
                else:                    
                    try:
                        msg = socket.recv(4096)                        
                        
                        if msg:                            
                            msg_header, msg_str = msg.decode().split('\x00')
                            
                            if msg_header == "CMD":
                                
                                if msg_str == "PIN CHECK":
                                    # get ready to receive pin
                                    
                                    socket.sendall(self.make_bytes_packet("ACK", "PIN CHECK"))                                    
                                    
                                    pin = socket.recv(4096)
                                    
                                    if pin:
                                        pin_header, pin_str = pin.decode().split('\x00')
                                        
                                        if pin_header == "DATA":                                                
                                            name = self.search_db(int(pin_str))
                                        
                                            if name:
                                                socket.sendall(self.make_bytes_packet("DATA", name))
                                            
                                            else:
                                                socket.sendall(self.make_bytes_packet("DATA", "PIN CHECK FAIL"))                                    
                                        
                            else:
                                socket.sendall(self.make_bytes_packet("ERROR", "INVALID PROTOCOL"))
                    
                    
                    except Exception as e:
                        socket.close()
                        self.client_sockets.remove(socket)
                        print(e)
                        #self.log.error(e)
                        continue
                        
    
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
    def make_bytes_packet(self, type, data):
        
        return ("{}\x00{}".format(type, data)).encode()
