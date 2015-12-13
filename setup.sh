#!/usr/bin/env bash

apt-get -y install libsoap-lite-perl python-pip
pip install -r "$(dirname "$0")/requirements.txt"
