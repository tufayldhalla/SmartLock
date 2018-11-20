import socket, sys
"""
DISTRIBUTED SYSTEM TEST MODULE: m_1
"""


class Mock1():
    
    def __init__(self):
        self.ID = 'D1'

        self.SERVER_ADDRESS = '192.168.0.21'
        self.PORT = 2018

    def connect_socket(self):

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.SERVER_ADDRESS, self.PORT))


    """
    TEST ID: m_1_1-1
    DESC: Test good passcode
    """
    def test_1_1_1(self):
        
        self.connect_socket()

        self.socket.sendall(self.make_packet("CMD", "PIN CHECK"))
        
        response = self.socket.recv(4096)
        
        response_header, response_str, response_sender = self.parse_packet(response)
        
        """
        try:
            assert response_header == "ACK", "GOT WRONG HEADER"
            assert response_str == "PIN CHECK", "GOT WRONG COMMAND"
            assert response_sender == "S", "GOT WRONG SENDER ID"
        
        except:
            print(sys.exc_info())
        """
        self.socket.sendall(self.make_packet("DATA", 8008))
        
        pin_check = self.socket.recv(4096)
        pin_check_header, pin_check_str, pin_check_sender = self.parse_packet(pin_check)
        

        try:
            assert pin_check_header == "DATA", "DID NOT RECEIVE DATA PACKET"
            assert pin_check_str == "bigdaddy6969", "GOT WRONG RESULT"
            assert pin_check_sender == "S", "GOT WRONG SENDER ID"
            print("(m_1_1-1) PASSED")

        except:
            print("(m_1_1-1) FAILED\n********\n{}".format(sys.exc_info()))
            print("********")
        
        finally:
            self.socket.close()


    """
    TEST ID: m_1_1-2
    DESC: Test bad passcode
    """
    def test_1_1_2(self):
        
        self.connect_socket()

        self.socket.sendall(self.make_packet("CMD", "PIN CHECK"))
        
        response = self.socket.recv(4096)
        
        response_header, response_str, response_sender = self.parse_packet(response)
        
        """
        try:
            assert response_header == "ACK", "GOT WRONG HEADER"
            assert response_str == "PIN CHECK", "GOT WRONG COMMAND"
            assert response_sender == "S", "GOT WRONG SENDER ID"
        
        except:
            print(sys.exc_info())
        """
        self.socket.sendall(self.make_packet("DATA", 8018))
        
        pin_check = self.socket.recv(4096)
        pin_check_header, pin_check_str, pin_check_sender = self.parse_packet(pin_check)
        

        try:
            assert pin_check_header == "DATA", "DID NOT RECEIVE DATA PACKET"
            assert pin_check_str == "PIN CHECK FAIL", "GOT WRONG RESULT"
            assert pin_check_sender == "S", "GOT WRONG SENDER ID"
            print("(m_1_1-2) PASSED")

        except:
            print("(m_1_1-2) FAILED\n********\n{}".format(sys.exc_info()))
            print("********")

        finally:
            self.socket.close()



    """
    TEST ID: m_1_1-3
    DESC: Test passcode fail 3 times
    """
    def test_1_1_3(self):
        
        self.connect_socket()

        self.socket.sendall(self.make_packet("CMD", "PIN CHECK"))
        
        response = self.socket.recv(4096)
        
        response_header, response_str, response_sender = self.parse_packet(response)
        
        """
        try:
            assert response_header == "ACK", "GOT WRONG HEADER"
            assert response_str == "PIN CHECK", "GOT WRONG COMMAND"
            assert response_sender == "S", "GOT WRONG SENDER ID"
        
        except:
            print(sys.exc_info())
        """
        self.socket.sendall(self.make_packet("DATA", 8018))
        
        pin_check = self.socket.recv(4096)
        pin_check_header, pin_check_str, pin_check_sender = self.parse_packet(pin_check)
        

        try:
            assert pin_check_header == "DATA", "DID NOT RECEIVE DATA PACKET"
            assert pin_check_str == "PIN CHECK FAIL", "GOT WRONG RESULT"
            assert pin_check_sender == "S", "GOT WRONG SENDER ID"
            print("(m_1_1-3) PASSED")

        except:
            print("(m_1_1-3) FAILED\n********\n{}".format(sys.exc_info()))
            print("********")

        finally:
            self.socket.close()


    """
    TEST ID: m_1_1-4
    DESC: Test incorrect protocol used
    """
    def test_1_1_4(self):
        
        self.connect_socket()

        self.socket.sendall(self.make_packet("DOLT", "PIN CHECK"))
        
        response = self.socket.recv(4096)
        
        response_header, response_str, response_sender = self.parse_packet(response)
        
        try:
            assert response_header == "ERROR", "DID NOT RECEIVE ERROR PACKET"
            assert response_str == "INVALID PROTOCOL", "GOT WRONG RESULT"
            assert response_sender == "S", "GOT WRONG SENDER ID"
            print("(m_1_1-4) PASSED")

        except:
            print("(m_1_1-4) FAILED\n********\n{}".format(sys.exc_info()))
            print("********")

        finally:
            self.socket.close()
              

        




    
    """UTILITY CLASSES"""


    def parse_packet(self, data):

        return data.decode().split('\x00')

    def make_packet(self, type, data):

        return ("{}\x00{}\x00{}".format(type, data, self.ID)).encode()


