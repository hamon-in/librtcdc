# Makefile
# Copyright (c) 2015 Xiaohan Song <chef@dark.kitchen>
# This file is licensed under a BSD license.

CFLAGS+=-Wl,--no-as-needed -g -O2 -DINET -DINET6 -DDEBUG_SCTP -fPIC -Wno-deprecated `pkg-config --cflags openssl nice` -I usrsctp/usrsctplib  
LDFLAGS+=`pkg-config --libs openssl nice` -L usrsctp/usrsctplib/.libs -lusrsctp -lpthread
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

all:  $(SOURCES) $(TARGET)

deps: 
	cd usrsctp && ./bootstrap && ./configure && make && cd ..

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -shared -fPIC $(LDFLAGS) $(OBJECTS) -o $@

.c.o:
	$(CC) -c $(CFLAGS) $< -o $@

clean:
	rm -f *.o *.so *.dylib *.a example && cd usrsctp && make clean && cd .. 

