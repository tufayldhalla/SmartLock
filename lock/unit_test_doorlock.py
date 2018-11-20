from doorlock import DoorLock
import sys, logging


class UnitTestDoorLock():

    def __init__(self):
        
        self.doorlock = DoorLock("D1", "y", "y")

        #self.test_make_packet()
        self.run_unit_tests()
        

    def run_unit_tests(self):
        self.test_make_packet()
        self.test_parse_packet()
        self.test_create_log()

    def test_make_packet(self):
        
        # test make DATA packet
        packet1 = self.doorlock.make_packet("DATA", "APPLE")
        
        # test make ERROR packet
        packet2 = self.doorlock.make_packet("ERROR", "BANANAS")
        
        # test make CMD packet
        packet3 = self.doorlock.make_packet ("CMD", "PEACHES")

        # test make ACK packet
        packet4 = self.doorlock.make_packet("ACK", "DATES")
        

        try:
            assert packet1 == "DATA\x00APPLE\x00D1".encode(), "FAILED (test_make_packet_1)"
            print("PASSED (test_make_packet_1)")
        except:
            print(sys.exc_info())


        try:
            assert packet2 == "ERROR\x00BANANAS\x00D1".encode(), "FAILED (test_make_packet_2)"
            print("PASSED (test_make_packet_2)")
        except:
            print(sys.exc_info())
            
        try:
            assert packet3 == "CMD\x00PEACHES\x00D1".encode(), "FAILED (test_make_packet_3)"
            print("PASSED (test_make_packet_3)")
        except:
            print(sys.exc_info())
            
        try:
            assert packet4 == "ACK\x00DATES\x00D1".encode(), "FAILED (test_make_packet_4)"
            print("PASSED (test_make_packet_4)")
        except:
            print(sys.exc_info())

        


    def test_parse_packet(self):
        packet1 = "DATA\x00ANGIE\x00D1".encode()
        packet2 = "ERROR\x00BANANAS\x00D1".encode()
        packet3 = "CMD\x00PEACHES\x00D1".encode()
        packet4 = "ACK\x00ADATES\x00D1".encode()
        
        try:
            assert self.doorlock.parse_packet(packet1) == ["DATA", "ANGIE", "D1"], "FAILED (test_parse_packet_1)"
            print("PASSED (test_parse_packet_1)")
        except:
            print(sys.exc_info())
            
        try:
            assert self.doorlock.parse_packet(packet2) == ["ERROR", "BANANAS", "D1"], "FAILED (test_parse_packet_2)"
            print("PASSED (test_parse_packet_2)")
        except:
            print(sys.exc_info())
            
        try:
            assert self.doorlock.parse_packet(packet3) == ["CMD", "PEACHES", "D1"], "FAILED (test_parse_packet_3)"
            print("PASSED (test_parse_packet_3)")
        except:
            print(sys.exc_info())
            
        try:
            assert self.doorlock.parse_packet(packet4) == ["ACK", "ADATES", "D1"], "FAILED (test_parse_packet_4)"
            print("PASSED (test_parse_packet_4)")
        except:
            print(sys.exc_info())



    def test_create_log(self):
        self.formatter = logging.Formatter("\%(asctime)s \%(levelname)s \%(identifier)s \%(message)s\n")


        try:
            raise ZeroDivisionError
        except:
            exc1 = sys.exc_info()

        try:
            assert self.doorlock.create_log(exc1) == self.formatter.formatException(exc1), "FAILED (test_create_log_1)"
            print("PASSED (test_create_log_1)")
        except:
            print(sys.exc_info())


        try:
            raise OverflowError
        except:
            exc2 = sys.exc_info()

        try:
            assert self.doorlock.create_log(exc2) == self.formatter.formatException(exc2), "FAILED (test_create_log_2)"
            print("PASSED (test_create_log_2)")
        except:
            print(sys.exc_info())

        try:
            raise KeyboardInterrupt
        except:
            exc3 = sys.exc_info()

        try:
            assert self.doorlock.create_log(exc3) == self.formatter.formatException(exc3), "FAILED (test_create_log_3)"
            print("PASSED (test_create_log_3)")
        except:
            print(sys.exc_info())



    


