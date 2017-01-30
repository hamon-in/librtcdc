from cffi import FFI
from time import sleep
import thread
from base64 import b64encode, b64decode
ffi = FFI()
RTCDC_CHANNEL_STATE_CLOSED = 0
RTCDC_CHANNEL_STATE_CONNECTING = 1
RTCDC_CHANNEL_STATE_CONNECTED = 2
RTCDC_DATATYPE_STRING = 0
ffi.cdef("""
            typedef void (*rtcdc_on_open_cb)(struct rtcdc_data_channel *channel, void *user_data);
            typedef void (*rtcdc_on_message_cb)(struct rtcdc_data_channel *channel, int datatype, void *data, size_t len, void *user_data);
            typedef void (*rtcdc_on_close_cb)(struct rtcdc_data_channel *channel, void *user_data);

            struct sctp_transport;
            typedef struct rtcdc_data_channel {
              uint8_t type;
              uint16_t priority;
              uint32_t rtx;
              uint32_t lifetime;
              char *label;
              char *protocol;
              int state;
              uint16_t sid;
              struct sctp_transport *sctp;
              rtcdc_on_open_cb on_open;
              rtcdc_on_message_cb on_message;
              rtcdc_on_close_cb on_close;
              void *user_data;
            } rtcdc_data_channel;
            
            typedef void (*rtcdc_on_channel_cb)(struct rtcdc_peer_connection *peer,
                                                struct rtcdc_data_channel *channel, void *user_data);

            typedef void (*rtcdc_on_candidate_cb)(struct rtcdc_peer_connection *peer,
                                                  const char *candidate, void *user_data);

            typedef void (*rtcdc_on_connect_cb)(struct rtcdc_peer_connection *peer, void *user_data);

            typedef struct rtcdc_peer_connection {
              char *stun_server;
              uint16_t stun_port;
              int exit_thread;
              struct rtcdc_transport *transport;
              int initialized;
              int role;
              struct rtcdc_data_channel *channels[128];
              rtcdc_on_channel_cb on_channel;
              rtcdc_on_candidate_cb on_candidate;
              rtcdc_on_connect_cb on_connect;
              void *user_data;
            } rtcdc_peer_connection;

            struct rtcdc_peer_connection *
            rtcdc_create_peer_connection(rtcdc_on_channel_cb, rtcdc_on_candidate_cb, rtcdc_on_connect_cb,
                                         const char *stun_server, uint16_t stun_port,
                                         void *user_data);

            void rtcdc_loop(struct rtcdc_peer_connection *peer);
            char* rtcdc_generate_offer_sdp(rtcdc_peer_connection *peer);
            char* rtcdc_generate_local_candidate_sdp(rtcdc_peer_connection *peer);

            int rtcdc_parse_offer_sdp(struct rtcdc_peer_connection *peer, const char *offer);
            int rtcdc_parse_candidate_sdp(struct rtcdc_peer_connection *peer, const char *candidates);
            struct rtcdc_data_channel *
            rtcdc_create_data_channel(struct rtcdc_peer_connection *peer,
                                      const char *label, const char *protocol,
                                      rtcdc_on_open_cb, rtcdc_on_message_cb, rtcdc_on_close_cb,
                                      void *user_data);

            void
            rtcdc_destroy_data_channel(struct rtcdc_data_channel *channel);

            int
            rtcdc_send_message(struct rtcdc_data_channel *channel, int datatype, void *data, size_t len);

            """)

@ffi.callback("void(rtcdc_data_channel*, void*)")
def onOpenCB(channel, userdata):
    ffi.from_handle(userdata)._onOpen(channel)

@ffi.callback("void(*)(rtcdc_data_channel*, int, void*, size_t, void*)")
def onMessageCB(channel, datatype, data, length, userdata):
    if datatype == RTCDC_DATATYPE_STRING:
        message = ffi.cast("char *", data)
        message = ffi.string(message)
        if userdata:
            ffi.from_handle(userdata)._onMessage(message[:length])

@ffi.callback("void(rtcdc_data_channel*, void*)")
def onCloseCB(channel, userdata):
    ffi.from_handle(userdata)._onClose(channel)

@ffi.callback("void(rtcdc_peer_connection*, rtcdc_data_channel*, void*)")
def onChannelCB(peer, dc, userdata):
    dc.on_message = onMessageCB
    dc.user_data = userdata
    ffi.from_handle(userdata)._onChannel(peer, dc)

@ffi.callback("void(rtcdc_peer_connection*, char*, void*)")
def onCandidateCB(peer, candidate, userdata):
    candidate = ffi.string(candidate)
    ffi.from_handle(userdata)._onCandidate(peer, candidate)

@ffi.callback("void(rtcdc_peer_connection*, void*)")
def onConnectCB(peer, userdata):
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
        self.C.rtcdc_create_data_channel(peer, self.dcName, self.protocol, onOpenCB, onMessageCB, onCloseCB, userdata)
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
        self.dcName = dcName
        self.protocol = protocol
        port = int(port)
        self.ffi = ffi
        
        self.C = self.ffi.dlopen("../src/vendor/build/librtcdc.so")
        self.peer = self.C.rtcdc_create_peer_connection(onChannelCB, onCandidateCB, onConnectCB, stunServer, port, self._handle)
        thread.start_new_thread(self.C.rtcdc_loop, (self.peer, ))

    def generate_offer_sdp(self):
        offerSDP = self.C.rtcdc_generate_offer_sdp(self.peer)
        offerSDP = self.ffi.string(offerSDP)
        return b64encode(offerSDP)

    def generate_local_candidate(self):
        candidateSDP = self.C.rtcdc_generate_local_candidate_sdp(self.peer)
        candidateSDP = self.ffi.string(candidateSDP)
        return b64encode(candidateSDP)

    def parse_offer_sdp(self, offerSDP):
        try:
            remoteSDP = str(b64decode(offerSDP))
        except TypeError:
            print "Invalid base64!"
        parse_offer = self.C.rtcdc_parse_offer_sdp(self.peer, remoteSDP)
        if parse_offer >= 0:
            return self.generate_offer_sdp()
        else:
            print "Error in parsing offer SDP"
            return None

    def parse_candidates(self, candidate):
        try:
            remoteCand = str(b64decode(candidate))
        except TypeError:
            print "Invalid base64!"
        parse_cand = self.C.rtcdc_parse_candidate_sdp(self.peer, remoteCand)
        return (parse_cand > 0)
    
    def send_message(self, message):
        if (self.peer[0].initialized > 0):
            if (self.dc_open == True and self.peer[0].channels[0].state > RTCDC_CHANNEL_STATE_CLOSED):
                channel = self.peer[0].channels[0]
                return (self.C.rtcdc_send_message(channel, RTCDC_DATATYPE_STRING, message, len(message)) == 0)
            else:
                return False
        else:
            return False
