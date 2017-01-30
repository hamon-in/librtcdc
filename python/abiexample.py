from cffi import FFI
from time import sleep

import thread
from base64 import b64encode, b64decode

dc_open = False

ffi = FFI()
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
C = ffi.dlopen("../src/vendor/build/librtcdc.so")
RTCDC_CHANNEL_STATE_CLOSED = 0
RTCDC_CHANNEL_STATE_CONNECTING = 1
RTCDC_CHANNEL_STATE_CONNECTED = 2
RTCDC_DATATYPE_STRING = 0
@ffi.callback("void(rtcdc_data_channel*, void*)")
def onOpen(channel, userdata):
    global dc_open
    print "Data Channel opened!"
    dc_open = True

@ffi.callback("void(*)(rtcdc_data_channel*, int, void*, size_t, void*)")
def onMessage(channel, datatype, data, length, userdata):
    message = ffi.cast("char *", data)
    print ""
    print "Message received: ", ffi.string(message)

@ffi.callback("void(rtcdc_data_channel*, void*)")
def onClose(channel, userdata):
    global dc_open
    print "Data channel closed."
    dc_open = False

@ffi.callback("void(rtcdc_peer_connection*, rtcdc_data_channel*, void*)")
def onChannelCB(peer, dc, userdata):
    dc.on_message = onMessage
    print "Channel created."

@ffi.callback("void(rtcdc_peer_connection*, char*, void*)")
def onCandidateCB(peer, candidate, userdata):
    pass
    #print "Candidate data: " + ffi.string(candidate)

@ffi.callback("void(rtcdc_peer_connection*, void*)")
def onConnectCB(peer, userdata):
    print "Peer connection established. Now opening the data channel through it..."
    C.rtcdc_create_data_channel(peer, "test-dc", "", onOpen, onMessage, onClose, "void *")

peer = C.rtcdc_create_peer_connection(onChannelCB, onCandidateCB, onConnectCB, "stun.services.mozilla.com", 3478,  "void *")
offersdp = C.rtcdc_generate_offer_sdp(peer)
offersdp = ffi.string(offersdp)
print ""
print "Offer SDP: " + b64encode(offersdp)

local_cand = C.rtcdc_generate_local_candidate_sdp(peer)
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
    parse_offer = C.rtcdc_parse_offer_sdp(peer, remote_sdp)
    if (parse_offer >= 0):
        new_offer = C.rtcdc_generate_offer_sdp(peer)
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

    parse_cand = C.rtcdc_parse_candidate_sdp(peer, remote_cand)
    if (parse_cand > 0):
        print "Valid candidates."
        break
    else:
        print "Invalid candidates"

thread.start_new_thread(C.rtcdc_loop, (peer, ))

while True:
    if (peer[0].initialized > 0):
        if (dc_open is True and peer[0].channels[0].state > RTCDC_CHANNEL_STATE_CLOSED):
            to_send = raw_input("Enter message to send: ")
            string_length = len(to_send)
            channel = peer[0].channels[0]
            C.rtcdc_send_message(channel, RTCDC_DATATYPE_STRING, to_send, string_length)
        else:
            sleep(1)
    else:
        sleep(1)
