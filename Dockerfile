FROM python:3.5.3
MAINTAINER DaikiShiroi <daikishiroi@gmail.com>

COPY . /zaifbot

WORKDIR /zaifbot/zaifbot/setup
RUN tar -xzf ta-lib-0.4.0-src.tar.gz
WORKDIR ta-lib
RUN ./configure --prefix=/usr
RUN make
RUN make install

WORKDIR /zaifbot
RUN pip install -r requirements.txt

RUN pip install -e .['talib']
