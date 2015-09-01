#!/bin/bash
whoami
apt-get update
apt-get -y install lxc lxc-templates cgroup-lite redir
echo "Downloading vagrant..."
cd /tmp && wget -q https://dl.bintray.com/mitchellh/vagrant/vagrant_1.7.4_x86_64.deb && dpkg -i vagrant_1.7.4_x86_64.deb
vagrant plugin install vagrant-lxc