#!/usr/bin/env bash

apt-get -y install libsoap-lite-perl mono-devel python-pip
pip install -r "$(dirname "$0")/requirements.txt"
