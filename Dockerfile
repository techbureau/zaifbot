FROM ubuntu:latest
MAINTAINER DaikiShiroi <daikishiroi@gmail.com>

RUN apt-get update

RUN apt-get install -y \
  build-essential \
  python-setuptools \
  python-dev \
  python-pip \
  gfortran \
  libopenblas-dev \
  liblapack-dev \
  pkg-config \
  wget \

RUN pip install numpy \
  scipy \
  pandas \
  patsy \
  statsmodels \

# TA-Lib
RUN cd /tmp; \
	wget http://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz; \
	tar -xzf ta-lib-0.4.0-src.tar.gz; \
	cd ta-lib; \
	./configure ; make; make install; \
	cd ..; \
	rm ta-lib-0.4.0-src.tar.gz; \
	rm -rf ta-lib
RUN pip install TA-Lib

RUN pip install zaifbot==0.0.5