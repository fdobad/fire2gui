#!/bin/bash

# this package messes matplotlib QtAgg
sudo apt-mark hold python3-matplotlib

sudo apt install xclip python3-venv python3-pip python3-pyqt5 qgis

# python virtual environment
mkdir -p ~/pyenv/qgis
python3 -m venv --system-site-packages ~/pyenv/qgis
. ~/pyenv/qgis/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
