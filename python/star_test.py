from datachannel import DataChannel
import unittest
from time import sleep

def onConnect(peer):
    print("OnConnect")

def handshake(a, b):
    newoffer = a.parse_offer_sdp(b.generate_offer_sdp())
    b.parse_offer_sdp(newoffer)
    a.parse_candidates(b.generate_local_candidate())
    b.parse_candidates(a.generate_local_candidate())

class TestRTC(unittest.TestCase):
    def setUp(self):
        self.a = DataChannel()
        self.b = DataChannel()
        self.c = DataChannel()
        
        self.a.onConnect = onConnect
        self.c.onConnect = onConnect

        # A -> B
        print("Creating A->B")
        handshake(self.a, self.b)
        # One onConnect would be fired for A->B now for both A and B
               
    def test_msg(self):
        sleep(260)
        #self.assertEqual(self.peerB.message, "test")

if __name__ == '__main__':
    unittest.main()
