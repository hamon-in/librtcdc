from pyrtcdc import ffi, lib
from time import sleep
from threading import Thread
from base64 import b64encode, b64decode
RTCDC_CHANNEL_STATE_CLOSED = 0
RTCDC_CHANNEL_STATE_CONNECTING = 1
RTCDC_CHANNEL_STATE_CONNECTED = 2
RTCDC_DATATYPE_STRING = 0
RTCDC_DATATYPE_BINARY = 1

@ffi.def_extern()
def onopen_cb(channel, userdata):
    ffi.from_handle(userdata)._onOpen(channel)

@ffi.def_extern()
def onmessage_cb(channel, datatype, data, length, userdata):
    if datatype == RTCDC_DATATYPE_STRING:
        message = ffi.cast("char *", data)
        message = ffi.string(message)
        message = message[:length].decode("UTF-8")
    if datatype == RTCDC_DATATYPE_BINARY:
        message = ffi.cast("char *", data)
        message = ffi.buffer(message, length)[:]
    if userdata:
            ffi.from_handle(userdata)._onMessage(message)

@ffi.def_extern()
def onclose_cb(channel, userdata):
    ffi.from_handle(userdata)._onClose(channel)

@ffi.def_extern()
def onchannel_cb(peer, dc, userdata):
    dc.on_message = lib.onmessage_cb
    dc.user_data = userdata
    ffi.from_handle(userdata)._onChannel(peer, dc)

@ffi.def_extern()
def oncandidate_cb(peer, candidate, userdata):
    candidate = ffi.string(candidate)
    ffi.from_handle(userdata)._onCandidate(peer, candidate)

@ffi.def_extern()
def onconnect_cb(peer, userdata):
    ffi.from_handle(userdata)._onConnect(peer, userdata)

class DataChannel():
    def _onOpen(self, channel):
        self.dc_open = True
        self.onOpen(channel)

    def _onMessage(self, message):
        self.onMessage(message)

    def _onClose(self, channel):
        self.dc_open = False
        self.onClose(channel)

    def _onChannel(self, peer, channel):
        self.dc_open = True
        self.onChannel(peer, channel)

    def _onCandidate(self, peer, candidate):
        self.onCandidate(peer, candidate)

    def _onConnect(self, peer, userdata):
        lib.rtcdc_create_data_channel(peer, self.dcName, self.protocol, lib.onopen_cb, lib.onmessage_cb, lib.onclose_cb, userdata)
        self.onConnect(peer)
    
    def onOpen(self, channel):
        pass

    def onMessage(self, message):
        pass

    def onClose(self, channel):
        pass

    def onChannel(self, peer, channel):
        pass

    def onCandidate(self, peer, candidate):
        pass

    def onConnect(self, peer):
        pass

    def __init__(self, dcName="test-dc", stunServer="stun.services.mozilla.com", port=3418, protocol=""):
        self._handle = ffi.new_handle(self)
        self.dc_open = False
        self.dcName = bytes(dcName)
        self.protocol = bytes(protocol)
        port = int(port)
        self.peer = lib.rtcdc_create_peer_connection(lib.onchannel_cb, lib.oncandidate_cb, lib.onconnect_cb, bytes(stunServer), port, self._handle)
        Thread(target=lib.rtcdc_loop, args=(self.peer, ),).start()

    def generate_offer_sdp(self):
        offerSDP = lib.rtcdc_generate_offer_sdp(self.peer)
        offerSDP = ffi.string(offerSDP)
        return b64encode(offerSDP)

    def generate_local_candidate(self):
        candidateSDP = lib.rtcdc_generate_local_candidate_sdp(self.peer)
        candidateSDP = ffi.string(candidateSDP)
        return b64encode(candidateSDP)

    def parse_offer_sdp(self, offerSDP):
        try:
            remoteSDP = b64decode(offerSDP)
        except TypeError:
            print("Invalid base64!")
        parse_offer = lib.rtcdc_parse_offer_sdp(self.peer, remoteSDP)
        if parse_offer >= 0:
            return self.generate_offer_sdp()
        else:
            print("Error in parsing offer SDP")
            return None

    def parse_candidates(self, candidate):
        try:
            remoteCand = b64decode(candidate)
        except TypeError:
            print("Invalid base64!")
        parse_cand = lib.rtcdc_parse_candidate_sdp(self.peer, remoteCand)
        return (parse_cand > 0)
    
    def send_message(self, message):
        length_msg = len(message)
        if type(message) is str:
            datatype = RTCDC_DATATYPE_STRING
            message = bytes(message)
        elif type(message) is bytes:
            datatype = RTCDC_DATATYPE_BINARY
        if (self.peer[0].initialized > 0):
            if (self.dc_open == True and self.peer[0].channels[0].state > RTCDC_CHANNEL_STATE_CLOSED):
                channel = self.peer[0].channels[0]
                return (lib.rtcdc_send_message(channel, datatype, message, length_msg) == 0)
            else:
                return False
        else:
            return False

    def destroy_peer_connection(self, peer):
	if (self.peer.initialized > 0 and peer.initialized > 0):
		lib.rtcdc_destroy_peer_connection(peer)
		return True
	return False

    def destroy_data_channel(self, channel):
	if (self.peer.initialized > 0):
            if (self.dc_open == True and channel.state > RTCDC_CHANNEL_STATE_CLOSED):
		lib.rtcdc_destroy_data_channel(channel)
		return True
	return False
