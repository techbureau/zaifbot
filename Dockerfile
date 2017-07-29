FROM python:3.5.3
MAINTAINER DaikiShiroi <daikishiroi@gmail.com>

COPY . /zaifbot

WORKDIR /zaifbot/zaifbot/setup
RUN ./install_ta_lib.sh

WORKDIR /zaifbot
RUN pip install -r requirements.txt
RUN pip install -e .
