#!/usr/bin/env bash
pip install cython
CFLAGS="-I../src" LDFLAGS="-L../src/usrsctp/usrsctplib/.libs" python setup.py build_ext -i
