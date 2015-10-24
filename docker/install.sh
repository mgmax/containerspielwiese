#!/bin/bash

# this is run on the VM to install docker

sudo apt-get install docker.io apparmor-profiles python-pip
sudo pip install termcolor docker-py docopt
