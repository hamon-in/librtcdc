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
        self.t = 0
    
    def onMessage(self, message):
        print("entering callback")
        if message[0:4] == "ping":
            print(message)
            self.send_message("pongpong "+message[4:])
            
        elif message[0:4] == "pong":
            print("pong recieved :: {}".format(message))
            m = message.split(" ")
            if m[1] == str(self.ping_counter):
                t2 = time.time()
                print(round_trip_time = t2-t1)
                self.pings[self.ping_counter] = [t1, t2, rount_trip_time]
                self.ping_counter += 1
    def onConnect(self, peer):
        self.ping(False)
                              

    def register_peer(self):
        put_register = requests.put("http://127.0.0.1:5000/register", data = {'sdp': self.sdp, 'uuid':self.dcName, 'cand': self.candidate})
                              
    def ping(self, recipient):
        t1 = time.time()
        self.send_message("ping {} {} {}".format(self.ping_counter, t1, self.dcName))
        #threading.Thread(target = time_out, args = (20,))
       

def perform_handshake (peer1, peer2):
    get_target1 = requests.get("http://127.0.0.1:5000/request", params = {'uuid': peer1.dcName})
    get_target2 = requests.get("http://127.0.0.1:5000/request", params = {'uuid': peer2.dcName})
    dict_peer1 = get_target1.json()
    dict_peer2 = get_target2.json()
    new_offer_sdp = peer2.parse_offer_sdp(dict_peer1['sdp'])
    peer1.parse_offer_sdp(new_offer_sdp)
    a = peer1.parse_candidates(dict_peer2['cand'])
    b = peer2.parse_candidates(dict_peer1['cand'])
    print("hand")
    if (a and b):
        print("Handshake done")
        return True
    else:
        return False

def time_out(timeout):
    time.sleep(timeout)
        

if __name__ =="__main__":
    a = Peer(dcName=uuid.uuid1().hex, send_ping = True)
    b = Peer(dcName=uuid.uuid1().hex)
    a.register_peer()
    b.register_peer()
    perform_handshake(a, b)
    

    
    
   




















        
# def create_slave_pool(num=1):
#     peer_list = []
#     for i in range(1, num+1):
#         peer_list.append("peerS{}".format(i))
#     return peer_list

# def negotiate(peer):
#     peer.parse_candidates(candidate_sdp_slave)
#     peer.parse_candidates(candidate_sdp_master)

# def send_ping(peer1, peer2):
#     peer1.send_message("ping")
# 	peerM.send_message(message)

# def send_pong(ping_num):
# 	message = 'pong'*ping_num
# 	message = uuid + message
    

# if args.kind == 'master':
# 	peerM = dc.DataChannel()
# 	offer_sdp_master = peerM.generate_offer_sdp()
# 	candidate_sdp_master = peerM.generate_candidate_sdp()
# 	print(uuid_master = uuid.uuid1())
# 	put_register = requests.put(args.sigServer + "/register", data = {'kind': 'master', 'sdp': offer_sdp_master, 'uuid': uuid_master.hex, 'cand': candidate_sdp_master})cw

# if args.kind == 'slave':
# 	slave_pool = create_slave_pool(args.poolsize)
# 	for slave in slave_pool:
# 		peerS = dc.DataChannel()
		
# 		dict_master = json.dumps(get_target)
#                 offer_sdp_slave = peerS.parse_offer_sdp(str(dict_master['sdp']))
# 		candidate_sdp_slave = peerS.generate_candidate_sdp()
# 		uuid_slave = uuid.uuid1()
# 		put_r = requests.put(args.sigServer + "/register", data = {'kind': 'slave', 'sdp': offer_sdp_slave, 'uuid': uuid_slave.hex, 'cand': candidate_sdp_slave})


