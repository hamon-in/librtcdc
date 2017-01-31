from _apilib import ffi, lib
from base64 import b64encode, b64decode



RTCDC_CHANNEL_STATE_CLOSED = 0
RTCDC_CHANNEL_STATE_CONNECTING = 1
RTCDC_CHANNEL_STATE_CONNECTED = 2
RTCDC_DATATYPE_STRING = 0


@ffi.def_extern()
def onopen_cb(channel, userdata):
    lib.rtcdc_on_open_cb(channel, userdata)
    global dc_open
    print "Data Channel opened!"
    dc_open = True

@ffi.def_extern()
def onmessage_cb(channel, datatype, data, length, userdata):
    lib.rtcdc_on_message_cb(channel, datatype, data, length, userdata)
    message = ffi.cast("char *", data)
    print ""
    print "Message received: ", ffi.string(message)

@ffi.def_extern()
def onclose_cb(channel, userdata):
    lib.rtcdc_on_close_cb(channel, userdata)
    global dc_open
    print "Data channel closed."
    dc_open = False

@ffi.def_extern()
def onchannel_cb(peer, dc, userdata):
    lib.rtcdc_on_channel_cb(peer, dc, userdata)
    dc.on_message = onMessage
    print "Channel created."

@ffi.def_extern()
def oncandidate_cb(peer, candidate, userdata):
    lib.rtcdc_on_candidate_cb(peer, candidate, userdata)
    pass
    #print "Candidate data: " + ffi.string(candidate)

@ffi.def_extern()
def onconnect_cb(peer, userdata):
    lib.rtcdc_on_connect_cb(peer, userdata)
    print "Peer connection established. Now opening the data channel through it..."
    lib.rtcdc_create_data_channel(peer, "test-dc", "", onopen_cb, onmesage_cb, onclose_cb, "void *")


peer = lib.rtcdc_create_peer_connection(onchannel_cb, oncandidate_cb, onconnect_cb, "stun.services.mozilla.com", 3478,  "void *")
offersdp = lib.rtcdc_generate_offer_sdp(peer)
offersdp = ffi.string(offersdp)
print ""
print "Offer SDP: " + b64encode(offersdp)

local_cand = C.rtcdc_generate_local_candidate_sdp(peer)
local_cand = ffi.string(local_cand)
print ""
print "Local Candidate: " + b64encode(local_cand)

