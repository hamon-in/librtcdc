from _apilib import ffi, lib
from base64 import b64encode, b64decode
from time import sleep
import thread

RTCDC_CHANNEL_STATE_CLOSED = 0
RTCDC_CHANNEL_STATE_CONNECTING = 1
RTCDC_CHANNEL_STATE_CONNECTED = 2
RTCDC_DATATYPE_STRING = 0

dc_open = False

@ffi.def_extern()
def onopen_cb(channel, userdata):
    global dc_open
    print "Data Channel opened!"
    dc_open = True

@ffi.def_extern()
def onmessage_cb(channel, datatype, data, length, userdata):
    message = ffi.cast("char *", data)
    print ""
    print "Message received: ", ffi.string(message)

@ffi.def_extern()
def onclose_cb(channel, userdata):
    global dc_open
    print "Data channel closed."
    dc_open = False

@ffi.def_extern()
def onchannel_cb(peer, dc, userdata):
    dc.on_message = lib.onmessage_cb
    print "Channel created."

@ffi.def_extern()
def oncandidate_cb(peer, candidate, userdata):
    pass
    #print "Candidate data: " + ffi.string(candidate)

@ffi.def_extern()
def onconnect_cb(peer, userdata):
    print "Peer connection established. Now opening the data channel through it..."
    lib.rtcdc_create_data_channel(peer, "test-dc", "", lib.onopen_cb, lib.onmessage_cb, lib.onclose_cb, "void *")


peer = lib.rtcdc_create_peer_connection(lib.onchannel_cb, lib.oncandidate_cb, lib.onconnect_cb, "stun.services.mozilla.com", 3478,  "void *")
offersdp = lib.rtcdc_generate_offer_sdp(peer)
offersdp = ffi.string(offersdp)
print ""
print "Offer SDP: " + b64encode(offersdp)

local_cand = lib.rtcdc_generate_local_candidate_sdp(peer)
local_cand = ffi.string(local_cand)
print ""
print "Local Candidate: " + b64encode(local_cand)

while True:
    print ""
    remote_sdp = raw_input("Enter SDP Offer in b64: ")
    try:
        remote_sdp = b64decode(remote_sdp).decode('UTF-8')
        remote_sdp = str(remote_sdp)
    except TypeError:
        print "Base64 Error! Enter valid base64 encoded SDP Offer"
        continue
    if (len(remote_sdp) < 1):
        print "Enter a valid SDP offer in base 64."
        continue
    parse_offer = lib.rtcdc_parse_offer_sdp(peer, remote_sdp)
    if (parse_offer >= 0):
        new_offer = lib.rtcdc_generate_offer_sdp(peer)
        new_offer = ffi.string(new_offer)
        new_offer = b64encode(new_offer)
        print ""
        print "New offer: " + new_offer
        break
    else:
        print "Invalid remote offer SDP"

while True:
    print ""
    remote_cand = raw_input("Enter remote candidate: ")
    remote_cand = b64decode(remote_cand).decode('UTF-8')
    remote_cand = str(remote_cand)

    parse_cand = lib.rtcdc_parse_candidate_sdp(peer, remote_cand)
    if (parse_cand > 0):
        print "Valid candidates."
        break
    else:
        print "Invalid candidates"

thread.start_new_thread(lib.rtcdc_loop, (peer, ))

while True:
    if (peer[0].initialized > 0):
        if (dc_open is True and peer[0].channels[0].state > RTCDC_CHANNEL_STATE_CLOSED):
            to_send = raw_input("Enter message to send: ")
            string_length = len(to_send)
            channel = peer[0].channels[0]
            lib.rtcdc_send_message(channel, RTCDC_DATATYPE_STRING, to_send, string_length)
        else:
            sleep(1)
    else:
        sleep(1)
