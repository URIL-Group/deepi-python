#! /bin/sh
#
# Set up script for a new DEEPi System

# Enable SSH
sudo touch /boot/ssh

# Enable camera
sudo sh -c "echo '[all] # Enabling camera' >> /boot/config.txt"
sudo sh -c "echo 'start_x=1' >> /boot/config.txt"
sudo sh -c "echo 'gpu_mem=256' >> /boot/config.txt"
#sudo sh -c "echo 'dissable_camera_led=1' >> /boot/config.txt"

# Update RPi
sudo apt-get -y update
sudo apt-get -y upgrade
sudo apt-get -y autoremove

# Install supporting packages
sudo apt-get -y install proftpd-basic # TODO: check out pureftp
# https://www.raspberrypi.com/documentation/computers/remote-access.html
sudo apt-get -y install ntp
sudo apt-get -y install ffmpeg
sudo apt-get -y install git
sudo apt-get -y install nginx

# Install Python
sudo apt-get -y install python3-setuptools python3-dev build-essential libpq-dev
sudo apt-get -y install python3-virtualenv
sudo apt-get -y install python3-picamera

# Install pip
sudo apt-get install python3-pip
python -m pip install --upgrade pip setuptools wheel build

# TODO: Downlaod DEEPi-Python module
git clone git@github.com:URIL-Group/deepi-python.git
python -m build 
python -m pip install ws4py flask
# TODO: install deepi-python 

# TODO: Set up deployment service

# TODO: Set up configuration
cp deepi.conf ~/deepi.conf
