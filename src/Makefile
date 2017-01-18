# Makefile
# Copyright (c) 2015 Xiaohan Song <chef@dark.kitchen>
# This file is licensed under a BSD license.

CFLAGS+=-Wl,--no-as-needed -g -O2 -DINET -DINET6 -DDEBUG_SCTP -fPIC -Wno-deprecated `pkg-config --cflags openssl nice` -I usrsctp/usrsctplib -std=gnu11
LDFLAGS+=`pkg-config --libs openssl` -L ./build -lnice -lgio-2.0 -lgobject-2.0 -lglib-2.0 -lusrsctp -lpthread 
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

.PHONY: clean

USRSCTP = ./usrsctp/usrsctplib/.libs/libusrsctp.so
LIBNICE = ./libnice/nice/.libs/libnice.so
DEPS = ./build/

$(USRSCTP):
	cd usrsctp && ./bootstrap && ./configure && make && cd ..

$(LIBNICE):
	cd libnice && ./autogen.sh && ./configure && make && cd ..

$(DEPS): $(USRSCTP) $(LIBNICE)
	cp -R ./usrsctp/usrsctplib/.libs/* ./build/ && cp -R ./libnice/nice/.libs/* ./build/ && cp librtcdc.so ./build/

main: $(TARGET) $(DEPS)
	$(CC) $(CFLAGS) -I ./ $(LDFLAGS) $(TARGET) main.c -o main

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -shared -fPIC $(LDFLAGS) $(OBJECTS) -o $@

.c.o:
	$(CC) -c $(CFLAGS) $< -o $@

clean:
	rm -f *.o *.so *.dylib *.a example build/* && cd usrsctp && make clean && cd ..

test: main
	LD_LIBRARY_PATH=build/ ./main

