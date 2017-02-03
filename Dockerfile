FROM ubuntu:xenial
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update
RUN apt-get install -qy iputils-ping
RUN apt-get install -qy netcat
RUN apt-get install -qy python
RUN apt-get install -qy python-dev
RUN apt-get install -qy python-pip

RUN apt-get install -qy libglib2.0-dev
RUN apt-get install -qy libnice-dev
RUN apt-get install -qy libtool
RUN apt-get install -qy autotools-dev
RUN apt-get install -qy automake
RUN apt-get install -qy gtk-doc-tools
RUN apt-get install -qy libssl-dev

RUN pip install cffi

ADD ./librtcdc/ /psl-librtcdc
WORKDIR /psl-librtcdc
RUN cd src && make
ENV LD_LIBRARY_PATH /psl-librtcdc/src/vendor/build
RUN cd python && python setup.py install

WORKDIR /psl-librtcdc/python
CMD python ./dc_test.py
