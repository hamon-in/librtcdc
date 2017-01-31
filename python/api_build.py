from cffi import FFI
from time import sleep

import thread
from base64 import b64encode, b64decode


dc_open = False

ffibuilder = FFI()

ffibuilder.cdef("""

extern "Python" void onmessage_cb(struct rtcdc_data_channel *, int, void *, size_t, void *);
extern "Python" void onopen_cb(struct rtcdc_data_channel *, void *);
extern "Python" void onclose_cb(struct rtcdc_data_channel *, void *);
extern "Python" void onconnect_cb(struct rtcdc_data_channel *, int, void *, size_t, void *);
extern "Python" void onchannel_cb(struct rtcdc_peer_connection *, struct rtcdc_data_channel *, void *);
extern "Python" void oncandidate_cb(struct rtcdc_peer_connection *,const char *, void *);

""")


ffibuilder.set_source("_apilib",
                      r"""
#include "rtcdc.h"
#include <stdint.h>

""",
include_dirs = ["../src/", "../src/usrsctp/usrsctplib/",
                "/usr/include/glib-2.0", "/usr/lib64/glib-2.0/include", "/usr/lib/x86_64-linux-gnu/glib-2.0/include"],
extra_compile_args=["-std=gnu11"],
                      libraries = ["rtcdc"],
                      library_dirs = ["../src/vendor/build"])

if __name__ == "__main__":
    ffibuilder.compile(verbose = True)
