# Makefile
# Copyright (c) 2015 Xiaohan Song <chef@dark.kitchen>
# This file is licensed under a BSD license.

CFLAGS+=-Wl,--no-as-needed -g -O0 -DINET -DINET6 -DDEBUG_SCTP -fPIC -Wno-deprecated `pkg-config --cflags glib-2.0 openssl nice` -pthread -I/usr/include/gupnp-igd-1.0 -I/usr/include/gupnp-1.0 -I/usr/include/gssdp-1.0 -I/usr/include/libsoup-2.4 -I/usr/include/libxml2 -I/usr/include/uuid -I usrsctp/usrsctplib -std=gnu11
LDFLAGS+=`pkg-config --libs openssl` -L ./vendor/build -lnice -lgio-2.0 -lgobject-2.0 -lglib-2.0 -lusrsctp -lpthread 
SOURCES=util.c dtls.c sctp.c ice.c sdp.c dcep.c rtcdc.c
OBJECTS=$(SOURCES:.c=.o)
NAME=rtcdc

ifeq "$(OS)" ""
	OS = $(shell uname -s)
endif

ifeq "$(OS)" "Darwin"
	TARGET=lib$(NAME).dylib
else
	TARGET=lib$(NAME).so
endif

all:  $(SOURCES) $(TARGET) main

.PHONY: clean deps finaldeps

LIB_USRSCTP = usrsctp/.built
LIB_USRSCTP_DIR = ./usrsctp/usrsctplib
# LIB_NICE = libnice/.built
# LIB_NICE_DIR = ./libnice/nice

deps: $(LIB_USRSCTP)
	rm -Rf vendor
	mkdir -p vendor/build
	cp -r $(LIB_USRSCTP_DIR)/.libs/* vendor/build
	#cp -r $(LIB_NICE_DIR)/.libs/* vendor/build
	cp $(LIB_USRSCTP_DIR)/libusrsctp.la vendor
	#cp $(LIB_NICE_DIR)/libnice.la vendor

finaldeps: $(TARGET)
	cp $(TARGET) vendor/build

$(LIB_USRSCTP): 
	cd usrsctp && ./bootstrap && env -u CFLAGS ./configure && make
	touch usrsctp/.built

#$(LIB_NICE):
#	cd libnice && ./autogen.sh && env -u CFLAGS ./configure && make
#	touch libnice/.built

main: finaldeps 
	$(CC) $(CFLAGS) -I ./ $(LDFLAGS) $(TARGET) main.c -o main

$(TARGET): $(OBJECTS) deps
	$(CC) $(CFLAGS) -shared -fPIC $(LDFLAGS) $(OBJECTS) -o $@

# .c.o:
# 	$(CC) -c $(CFLAGS) $< -o $@

clean:
	rm -Rf vendor
	rm *.dylib ! $(LIB_USRSCTP)
	rm -f *.o *.so *.dylib *.a example  && cd usrsctp && make clean && cd ..

test: main
	LD_LIBRARY_PATH=vendor/build/ ./main
