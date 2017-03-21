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
from multiprocessing import Process, Pipe
import multiprocessing as mp
from time import sleep

def onMessage(self, msg):
    print("onMessage callback fired!")
    if (msg[:5] == "ping:"):
        peer.send_message("pong:" + msg[5:])
    if (msg[:5] == "pong:"):
        params = msg[5:].split(" ")
        pingtime = params[0]
        pingCounter = params[1]
        if pingCounter in peer.pings:
            print("Latency: ", str(time.time() - float(pingtime)))
    if (msg[:7] == "digest:"):
        peer.digest = msg[7:]
    if (type(msg) == bytes):
        with open("received", 'a+b') as fh:
            fh.write(msg)
    if (msg == "EOF"):
        print("Checking hash of received file...")
        if (peer.digest == fileDigest("received")):
            print("CHECKSUM OK")
        print("EOF received. deleting file")
        os.remove("received")

def second_peer(inp, out):
    peer = DataChannel(protocol="testprotocol")
    peer.pingCounter = 0
    peer.pings = {}
    peer.digest = None
    
    peer.onMessage = onMessage
    
    while True:
        msg = inp.recv() # will block
        if msg[0] == "sdp":
            newoffer = peer.parse_offer_sdp(msg[1])
            out.send(("newoffer", newoffer))
        if msg[0] == "cand":
            peer.parse_candidates(msg[1])
            out.send(("cand", peer.generate_local_candidate()))
        if msg[0] == "getmsg":
            out.send(peer.message_queue.get())

def send_random_payload(peer, size):
        # Size is in bytes
        print("Writing {} file".format(sizeof_fmt(size, suffix='B')))
        create_file("testfile", size)
        filehash = fileDigest("testfile")
        print("Wrote file. Digest: " + filehash)
        peer.send_message("digest:" + filehash)
        with open("testfile", "rb") as fh:
            chunksize = 10 #
            bufcount = 1
            buf = fh.read(chunksize)
            print("Sending {}".format(sizeof_fmt(len(buf), suffix='B')))
            peer.send_message(bytes(buf))
            while len(buf) > 0:
                bufcount += 1
                buf = fh.read(chunksize)
                if len(buf) == 0:
                    break
                print("Sending {} out of {}".format(sizeof_fmt(len(buf) * bufcount, suffix='B'), sizeof_fmt(size, suffix='B')))
                peer.send_message(bytes(buf))
            print("Sending EOF")
            peer.send_message("EOF")

def create_file(filename, size_bytes):
    chunksize = 10
    chunks = math.ceil(size_bytes / chunksize)
    with open(filename,"wb") as fh:
        for iter in range(chunks):
            numrand = os.urandom(int(size_bytes*chunksize / chunks))
            fh.write(numrand)
        numrand = os.urandom(int(size_bytes*chunksize % chunks))
        fh.write(numrand)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def fileDigest(file_name):
    BLOCKSIZE = 10
    #BLOCKSIZE = 65536 * 3
    hasher = hashlib.sha1()
    with open(file_name, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return (hasher.hexdigest())
                
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

def main():
    try:
        os.remove("testfile")
        os.remove("received")
    except FileNotFoundError:
        pass
    peer = DataChannel(protocol="testprotocol")
    peer.pingCounter = 0
    peer.pings = {}
    peer.digest = None
    sdp = peer.generate_offer_sdp()
    cand = peer.generate_local_candidate()
    ctx = mp.get_context("spawn")
    pipe1_A, pipe1_B = Pipe() # Used to send stuff to child
    pipe2_A, pipe2_B = Pipe() # Used to receive from child 
    p = ctx.Process(target=second_peer, args=(pipe1_B, pipe2_B))
    p.start()
    def onOpen(channel):
        #global peer
        #peer.t = perpetualTimer(1, sendPing, peer)
        #peer.t.start()
        size_list = [10, 100, 500, 1 * 1024, 5 * 1024, 10 * 1024, 20 * 1024, 50 * 1024, 100 * 1024, 500 * 1024, 1 * 1024 * 1024]
        for i in range(len(size_list)):
            send_random_payload(peer, size_list[i])
    peer.onOpen = onOpen
    # Handshake
    pipe1_A.send(("sdp", sdp))
    newoffer = pipe2_A.recv()
    newoffer = newoffer[1]
    peer.parse_offer_sdp(newoffer)
    pipe1_A.send(("cand", cand)) #
    recv_cand = pipe2_A.recv()
    recv_cand = recv_cand[1]
    peer.parse_candidates(recv_cand)
    p.join()

if __name__ == '__main__':
    main()
