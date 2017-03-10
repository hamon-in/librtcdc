from datachannel import DataChannel
import requests
import argparse
import math
import uuid
import sys
import os
import time
import hashlib
from threading import Timer,Thread,Event

parser = argparse.ArgumentParser()
parser.add_argument("sigServer", help="IP:port of signalling server")

args = parser.parse_args()

peer = DataChannel(protocol="testprotocol")
peer.pingCounter = 0
peer.pings = {}
peer.digest = None

sdp = peer.generate_offer_sdp()
cand = peer.generate_local_candidate()
uuid = uuid.uuid4()
print("My UUID: ", uuid.hex)
put_r = requests.put(args.sigServer + "/register", data = {'sdp': sdp, 'uuid': uuid.hex, 'cand': cand})

target_uuid = input("Enter target UUID4 (hex): ")
get_target = requests.get(args.sigServer + "/request", params = {'uuid': target_uuid })

try:
    target = get_target.json()
except ValueError:
    print("Could not find ", args.target)
    sys.exit(1)

def create_file(filename, size_kb):
    chunksize = 1024
    chunks = math.ceil(size_kb / chunksize)
    with open(filename,"wb") as fh:
        for iter in range(chunks):
            numrand = os.urandom(int(size_kb*1024 / chunks))
            fh.write(numrand)
        numrand = os.urandom(int(size_kb*1024 % chunks))
        fh.write(numrand)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def onOpen(channel):
    global peer
    #peer.t = perpetualTimer(1, sendPing, peer)
    #peer.t.start()
    size = 1024
    if (peer.peer.role == 1):
        for i in range(2, 3):
            size **= i
            send_random_payload(size)

def fileDigest(file_name):
    BLOCKSIZE = 65536 * 3
    hasher = hashlib.sha1()
    with open(file_name, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return (hasher.hexdigest())

def send_random_payload(size):
    # Size is in bytes
    print("Writing {} file".format(sizeof_fmt(size, suffix='B')))
    create_file("testfile", size / 1024)
    filehash = fileDigest("testfile")
    print("Wrote file. Digest: " + filehash)
    peer.send_message("digest:" + filehash)
    with open("testfile", "rb") as fh:
        chunksize = 6553
        bufcount = 1
        buf = fh.read(chunksize)
        print("Sending {}".format(sizeof_fmt(len(buf), suffix='B')))
        peer.send_message(bytes(buf))
        while len(buf) > 0:
            bufcount += 1
            buf = fh.read(chunksize)
            print("Sending {} out of {}".format(sizeof_fmt(len(buf) * bufcount, suffix='B'), sizeof_fmt(size, suffix='B')))
            peer.send_message(bytes(buf))
        print("Sending EOF")
        peer.send_message("EOF")
        
def sendPing(peer):
    if (peer.peer.role == 1):
        curr_time = str(time.time())
        peer.send_message("ping:" + curr_time + " " + str(peer.pingCounter))
        peer.pings[str(peer.pingCounter)] = curr_time
        peer.pingCounter += 1

class perpetualTimer():
   def __init__(self,t,hFunction, arg):
      self.t=t
      self.arg=arg
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function, [arg])

   def handle_function(self, arg):
      self.hFunction(arg)
      self.thread = Timer(self.t, self.handle_function, [arg])
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

def onMessage(msg):
    global peer
    if (peer.peer.role == 2):
        if (msg[:5] == "ping:"):
            # Reflect it
            peer.send_message("pong:" + msg[5:])
    if (msg[:5] == "pong:"):
        # Calculate RTT
        params = msg[5:].split(" ")
        pingtime = params[0]
        pingCounter = params[1]
        if pingCounter in peer.pings:
            print("Latency: ", str(time.time() - float(pingtime)))
    if (msg[:7] == "digest:"):
        peer.digest = msg[7:]
    if (type(msg) == bytes):
        # append to a file
        with open("received", 'wb') as fh:
            fh.write(msg)
    if (msg == "EOF"):
        print("Checking hash of received file...")
        if (peer.digest == fileDigest("received")):
            print("CHECKSUM OK")

peer.onOpen = onOpen
peer.onMessage = onMessage

sdp = peer.parse_offer_sdp(target["sdp"])
put_r = requests.put(args.sigServer + "/register", data = {'sdp': sdp, 'uuid': uuid.hex, 'cand': cand})
peer.parse_candidates(target["cand"])
