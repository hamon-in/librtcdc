# Makefile
# Copyright (c) 2015 Xiaohan Song <chef@dark.kitchen>
# This file is licensed under a BSD license.

CFLAGS+=-Wl,--no-as-needed -g -O2 -DINET -DINET6 -DDEBUG_SCTP -fPIC -Wno-deprecated `pkg-config --cflags openssl nice` -I usrsctp/usrsctplib -std=gnu11
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

all:  $(SOURCES) $(TARGET) main.c

deps: 
	cd usrsctp && ./bootstrap && ./configure && make && cd ..

main.c: $(TARGET)
	$(CC) $(CFLAGS) -I ./ $(LDFLAGS) $(TARGET) main.c -o main

$(TARGET): $(OBJECTS)
	$(CC) $(CFLAGS) -shared -fPIC $(LDFLAGS) $(OBJECTS) -o $@

.c.o:
	$(CC) -c $(CFLAGS) $< -o $@

clean:
	rm -f *.o *.so *.dylib *.a example && cd usrsctp && make clean && cd ..

test: main.c
	LD_LIBRARY_PATH=usrsctp/usrsctplib/.libs/:./ ./main

