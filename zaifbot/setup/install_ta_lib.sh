#!/bin/sh

tar -xzf setup/ta-lib-0.4.0-src.tar.gz -C setup/;
cd setup/ta-lib/;
./configure;
make;
sudo make install;