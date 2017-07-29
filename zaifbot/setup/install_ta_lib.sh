#!/bin/sh
pwd;
tar -xzf ta-lib-0.4.0-src.tar.gz;
cd ta-lib;
./configure --prefix=/usr;
make;
make install;