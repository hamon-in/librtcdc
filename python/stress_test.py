import datachannel as dc
import unittest
from time import sleep
from threading import Thread

MAX_CHANNELS = 128

class Peer(dc.DataChannel):
    def onMessage(self, message):
        print("MSG: " + message)

# TODO: Plot CPU, mem, 

def create_peers(peer_list, i):
    peer1 = Peer()
    peer2 = Peer()
    
    peer1_offersdp = peer1.generate_offer_sdp()
    peer1_candidatesdp = peer1.generate_local_candidate()

    peer2_newoffersdp = peer2.parse_offer_sdp(peer1_offersdp)
    peer2_candidatesdp = peer2.generate_local_candidate()

    peer1.parse_offer_sdp(peer2_newoffersdp)
    
    if peer1.parse_candidates(peer2_candidatesdp) and peer2.parse_candidates(peer1_candidatesdp):
        peer_tup = (peer1, peer2)
        print("Adding peer tuple #%d" % i)
        peer_list.insert(i, peer_tup)


class TestPeer(unittest.TestCase):
    peer_list = []
    def setUp(self):
        print("Max channels are %d" % MAX_CHANNELS)
        for i in range(1, int((MAX_CHANNELS) / 2) + 1):
            thread1 = Thread(target=create_peers, args=(self.peer_list, i, ), )
            thread1.start()
            thread1.join()
            
    def test_created(self):
        self.assertEqual(len(self.peer_list), MAX_CHANNELS / 2)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
