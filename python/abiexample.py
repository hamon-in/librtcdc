from cffi import FFI
ffi = FFI()
ffi.cdef("""    
    typedef void (*rtcdc_on_open_cb)(struct rtcdc_data_channel *channel, void *user_data);

    typedef void (*rtcdc_on_message_cb)(struct rtcdc_data_channel *channel,
                                        int datatype, void *data, size_t len, void *user_data);

    typedef void (*rtcdc_on_close_cb)(struct rtcdc_data_channel *channel, void *user_data);

    struct sctp_transport;
    struct rtcdc_data_channel {
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
    };
    
    typedef struct rtcdc_peer_connection;
    typedef struct rtcdc_data_channel;
    typedef void (*rtcdc_on_channel_cb)(struct rtcdc_peer_connection *peer,
                                        struct rtcdc_data_channel *channel, void *user_data);

    typedef void (*rtcdc_on_candidate_cb)(struct rtcdc_peer_connection *peer,
                                          const char *candidate, void *user_data);

    typedef void (*rtcdc_on_connect_cb)(struct rtcdc_peer_connection *peer, void *user_data);

    struct rtcdc_peer_connection {
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
    };    
    struct rtcdc_peer_connection *
    rtcdc_create_peer_connection(rtcdc_on_channel_cb, rtcdc_on_candidate_cb, rtcdc_on_connect_cb,
                                 const char *stun_server, uint16_t stun_port,
                                 void *user_data);
    """)
C = ffi.dlopen("../src/vendor/build/librtcdc.so")

@ffi.callback("void(rtcdc_peer_connection, rtcdc_data_channel, void)")
def onChannelCB(peer, dc, userdata):
    print "Channel created"

@ffi.callback("void(rtcdc_peer_connection, char*, void)")
def onCandidateCB(peer, candidate, userdata):
    print "Candidate: ", candidate

@ffi.callback("void(rtcdc_peer_connection, void)")
def onConnectCB(peer, userdata):
    print "OnConnect"

userdata = ffi.new("void *", "")
returnval = C.rtcdc_create_peer_connection(onChannelCB, onCandidateCB, onConnectCB, "stun.services.mozilla.com", 3478,  userdata)
print returnval
while True:
    sleep(3)
