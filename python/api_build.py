from cffi import FFI
from time import sleep

import thread
from base64 import b64encode, b64decode


dc_open = False

ffibuilder = FFI()


ffibuilder.set_source("_apilib",
                      r"""
#include <sys/types.h>
#include <rtcdc.h>
#include <dcep.h>
#include <sctp.h>
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS
#include <WinSock2.h>
#include <WS2tcpip.h>
#include <crtdbg.h>
#else
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <unistd.h>
#include <stdint.h>
#endif
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS
#include <WinSock2.h>
#include <WS2tcpip.h>
#include <crtdbg.h>
#else
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <unistd.h>
#include <stdint.h>
#endif
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>


struct rtcdc_data_channel *
rtcdc_create_data_channel(struct rtcdc_peer_connection *peer,
                          const char *label, const char *protocol,
                          rtcdc_on_open_cb on_open,
                          rtcdc_on_message_cb on_message,
                          rtcdc_on_close_cb on_close,
                          void *user_data)
{
  if (peer == NULL || peer->transport == NULL || peer->channels == NULL)
    return NULL;

                      struct rtcdc_transport *transport = peer->transport;
  struct sctp_transport *sctp = transport->sctp;

  int i;
  for (i = 0; i < RTCDC_MAX_CHANNEL_NUM; ++i) {
    if (peer->channels[i])
      continue;
    break;
  }

  if (i == RTCDC_MAX_CHANNEL_NUM)
    return NULL;

  struct rtcdc_data_channel *ch = (struct rtcdc_data_channel *)calloc(1, sizeof *ch);
  if (ch == NULL)
    return NULL;
  ch->on_open = on_open;
  ch->on_message = on_message;
  ch->on_close = on_close;
  ch->user_data = user_data;
  ch->sctp = sctp;

  struct dcep_open_message *req;
  int rlen = sizeof *req + strlen(label) + strlen(protocol);
  req = (struct dcep_open_message *)calloc(1, rlen);
  if (req == NULL)
    goto open_channel_err;

  ch->type = DATA_CHANNEL_RELIABLE;
  ch->state = RTCDC_CHANNEL_STATE_CONNECTING;
  if (label)
    ch->label = strdup(label);
  if (protocol)
    ch->protocol = strdup(protocol);
  ch->sid = sctp->stream_cursor;
  sctp->stream_cursor += 2;

  req->message_type = DATA_CHANNEL_OPEN;
  req->channel_type = ch->type;
  req->priority = htons(0);
  req->reliability_param = htonl(0);
  if (label)
    req->label_length = htons(strlen(label));
  if (protocol)
    req->protocol_length = htons(strlen(protocol));
  memcpy(req->label_and_protocol, label, strlen(label));
  memcpy(req->label_and_protocol + strlen(label), protocol, strlen(protocol));

  int ret = send_sctp_message(sctp, req, rlen, ch->sid, WEBRTC_CONTROL_PPID);
  free(req);
  if (ret < 0)
    goto open_channel_err;

  if (0) {
open_channel_err:
    free(ch);
    ch = NULL;
  }

  peer->channels[i] = ch;
  return ch;
}


struct rtcdc_peer_connection *
rtcdc_create_peer_connection(rtcdc_on_channel_cb on_channel,
                             rtcdc_on_candidate_cb on_candidate,
                             rtcdc_on_connect_cb on_connect,
                             const char *stun_server, uint16_t stun_port,
                             void *user_data)
{
  char buf[INET_ADDRSTRLEN];
  if (stun_server != NULL && strcmp(stun_server, "") != 0) {
    memset(buf, 0, sizeof buf);
    struct addrinfo hints, *servinfo;
    memset(&hints, 0, sizeof hints);
    hints.ai_family = AF_INET;
    
    if ((getaddrinfo(stun_server, NULL, &hints, &servinfo)) != 0)
      return NULL;

    struct sockaddr_in *sa = (struct sockaddr_in *)servinfo->ai_addr;
    inet_ntop(AF_INET, &(sa->sin_addr), buf, INET_ADDRSTRLEN);
    freeaddrinfo(servinfo);
  }

  struct rtcdc_peer_connection *peer =
    (struct rtcdc_peer_connection *)calloc(1, sizeof *peer);
  if (peer == NULL)
    return NULL;
  if (stun_server)
    peer->stun_server = strdup(buf);
  peer->stun_port = stun_port > 0 ? stun_port : 3478;
  peer->on_channel = on_channel;
  peer->on_candidate = on_candidate;
  peer->on_connect = on_connect;
  peer->user_data = user_data;

  return peer;
}""",
include_dirs = ["../src/", "../src/usrsctp/usrsctplib/",
                "/usr/include/glib-2.0", "/usr/lib64/glib-2.0/include", "/usr/lib/x86_64-linux-gnu/glib-2.0/include"])

RTCDC_CHANNEL_STATE_CLOSED = 0
RTCDC_CHANNEL_STATE_CONNECTING = 1
RTCDC_CHANNEL_STATE_CONNECTED = 2
RTCDC_DATATYPE_STRING = 0

if __name__ == "__main__":
    ffibuilder.compile(verbose = True)
