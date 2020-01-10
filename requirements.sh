#!/bin/bash

if [ "$EUID" -ne 0 ]
    then echo "Please run as root."
    exit
fi

apt install tor python3 python3-pip
pip3 install requests
pip3 install requests[socks]
pip3 install eventlet
pip3 install socket
pip3 install socks
pip3 install stem
pip3 install csv
pip3 install subprocess
