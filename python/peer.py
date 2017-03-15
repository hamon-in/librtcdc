# This prints a UUID when started, registers with signalling server.
# Arguments: signalling server.
# Target UUID to be passed to stdin.
# On Receiving a message in text: message:\n'something'
# On Receiving a binary message: message:\nb'something'

from datachannel import DataChannel
import argparse
import uuid
import requests

def onMessage(msg):
    print("message:")
    print(msg)

def onOpen(channel):
    print("onopen")

def onConnect(peer):
    print("onconnect")

def onClose(channel):
    print("onclose")

def onChannel(peer, channel):
    print("onchannel")

def onCandidate(peer, candidate):
    print("oncandidate")

parser = argparse.ArgumentParser()
parser.add_argument("sigServer", help="IP:port of signalling server")

args = parser.parse_args()

peer = DataChannel()

sdp = peer.generate_offer_sdp()
cand = peer.generate_local_candidate()
uuid = uuid.uuid4()
print("My UUID: ", uuid.hex) #STDOUT
put_r = requests.put(args.sigServer + "/register", data = {'sdp': sdp, 'uuid': uuid.hex, 'cand': cand})

target_uuid = input() #STDIN
get_target = requests.get(args.sigServer + "/request", params = {'uuid': target_uuid })

try:
    target = get_target.json()
except ValueError:
    print("Could not find ", args.target)
    sys.exit(1)

peer.onOpen = onOpen
peer.onMessage = onMessage
peer.onConnect = onConnect
peer.onClose = onClose
peer.onChannel = onChannel
peer.onCandidate = onCandidate

sdp = peer.parse_offer_sdp(target["sdp"])
put_r = requests.put(args.sigServer + "/register", data = {'sdp': sdp, 'uuid': uuid.hex, 'cand': cand})
peer.parse_candidates(target["cand"])
