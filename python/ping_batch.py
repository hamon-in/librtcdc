import datachannel as dc
import time
import argparse
import requests
import uuid
import json
import threading

class Peer(dc.DataChannel):
    "This is a peer that creates a channel once negotiation is successful"
    def __init__ (self, dcName, send_ping = False):
        super().__init__(dcName)
        self.sdp = self.generate_offer_sdp()
        self.candidate = self.generate_local_candidate()
        self.ping_counter = 1
        self.pings = {}
        self.target = None
        self.size = 1
        self.batchsize = 1
    
    def onMessage(self, message):
        print("entering callback")
        if message[0:4] == "ping":
            print(message)
            self.send_message("pong"+message[4:])
            
        elif message[0:4] == "pong":
            print("pong recieved :: {}".format(message))
            m = message.split(" ")
            #if int(m[1]) in self.pings.keys():
            print("entering pong parser")
            t1 = float(m[2])
            t2 = time.time()
            print(t2)
            print("round_trip_time = ", t2-t1)
            round_trip_time = t2-t1
            self.pings[int(m[1])] = round_trip_time
            print(self.pings)
                
    def onConnect(self, peer):
        pass

    def onOpen(self, channel):
        if self.peer.role == 1 and self.target != None:
            # Once the channel opens, the callback sends batch of pings
            # The process causes significant delay even when a batch of size 2 is sent.
            for i in range(1, self.batchsize+1):
                ping_count = i
                self.ping(self.target, ping_count)

                

    def register_peer(self):
        put_register = requests.put("http://127.0.0.1:5000/register", data = {'sdp': self.sdp, 'uuid':self.dcName, 'cand': self.candidate})
                              
    def ping(self, recipient, ping_count):
        t1 = time.time()
        self.send_message("ping {} {} {} ".format(ping_count, t1, self.dcName)*self.size)

def perform_handshake (peer1, peer2):
    get_target1 = requests.get("http://127.0.0.1:5000/request", params = {'uuid': peer1.dcName})
    get_target2 = requests.get("http://127.0.0.1:5000/request", params = {'uuid': peer2.dcName})
    dict_peer1 = get_target1.json()
    dict_peer2 = get_target2.json()
    new_offer_sdp = peer2.parse_offer_sdp(dict_peer1['sdp'])
    peer1.parse_offer_sdp(new_offer_sdp)
    a = peer1.parse_candidates(dict_peer2['cand'])
    b = peer2.parse_candidates(dict_peer1['cand'])
    if (a and b):
        print("Handshake done")
        return True
    else:
        return False
        

if __name__ =="__main__":
    a = Peer(dcName=uuid.uuid1().hex, send_ping = True)
    b = Peer(dcName=uuid.uuid1().hex)
    a.size = int(input("Enter the number of packets to be sent > ")) # A packet is of 62 charachter length
    a.batchsize = int(input("Enter the size of the batch > "))
    a.target = b
    a.register_peer()
    b.register_peer()
    perform_handshake(a, b)

def init():
    a = Peer(dcName=uuid.uuid1().hex, send_ping = True)
    b = Peer(dcName=uuid.uuid1().hex)
    a.register_peer()
    b.register_peer()
    perform_handshake(a, b)
    return a,b
    

    

    
    
   











