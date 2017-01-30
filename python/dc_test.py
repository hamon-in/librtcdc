import datachannel as dc
import unittest
from time import sleep

class PeerA(dc.DataChannel):
    def onChannel(self, peer, channel):
        print "DC opened, sending a test msg"
        self.send_message("test")

class PeerB(dc.DataChannel):
    def onMessage(self, message):
        print "PeerB received: " + message
        self.message = message

class TestRTC(unittest.TestCase):
    def setUp(self):
        self.peerA = PeerA()
        self.offerSDP_A = self.peerA.generate_offer_sdp()
        self.candidateSDP_A = self.peerA.generate_local_candidate()

        self.peerB = PeerB()
        self.new_offerSDPofB = self.peerB.parse_offer_sdp(self.offerSDP_A)
        self.candidateSDP_B = self.peerB.generate_local_candidate()

        self.peerA.parse_offer_sdp(self.new_offerSDPofB)

        self.peerAPC = self.peerA.parse_candidates(self.candidateSDP_B)
        self.peerBPC = self.peerB.parse_candidates(self.candidateSDP_A)

    def test_parse_candidates(self):
        self.assertTrue(self.peerAPC)
        self.assertTrue(self.peerBPC)

    def test_msg(self):
        sleep(7)
        self.assertEqual(self.peerB.message, "test")

if __name__ == '__main__':
    unittest.main()
