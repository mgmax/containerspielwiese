#!/bin/bash
whoami

echo 'deb http://ubuntu.zerogw.com vagga main' | sudo tee /etc/apt/sources.list.d/vagga.list
sudo apt-get update
sudo apt-get -y --force-yes install vagga
sudo -u vagrant mkdir /home/vagrant/vagga/
sudo -u vagrant cp  /share/vagga.yaml /home/vagrant/vagga
sudo -u vagrant cp -r /share/data /home/vagrant/vagga
