#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""

depends on
docker-py
and TODO...

"""

from __future__ import print_function
import docker
import json
import sys
import logging
from time import sleep
import requests
import subprocess
import socket
import time
import datetime

c = docker.Client(base_url='unix://var/run/docker.sock', version='1.12')

class AbstractContainer(object):
    pass
    
class DockerContainer(AbstractContainer):
    def __init__(self, name, path, docker_options="", tests=None):
        """
        :param options: commandline options to 'docker run'
        :param tests: dictionary {'sleep_before': <sleep time>, 'http': <list of http(s) URLs that must return HTTP OK>, 'port': <list of ports that must be listening>}
        """
        self.name = name
        self.image_name = self.name + ':latest'
        self.path = path
        self.docker_options = docker_options
        self._tests = tests if tests else {}
        pass
    
    def rebuild(self):
        # self.is_running() is called for the check against manually started containers from this image
        # after building, the old images will be nameless and this check is no longer possible
        self.is_running()
        
        for line in c.build(self.path, rm=True, container_limits={'memory':1e9}, tag=self.image_name):
            # line is something like '{"stream":" ---\u003e Using cache\n"}'
            sys.stdout.write(json.loads(line).get('stream',''))
    
    def running_container_id(self):
        """ return id of last known container instance, or False otherwise"""
        try:
            f = open(self.name + '.running_container_id', 'r')
            return f.read()
        except IOError:
            return False
    
    def _set_running_container_id(self, new_id):
        
        previous_id = self.running_container_id()
        logging.info("previous '{}' container id was: {}".format(self.name, previous_id))
        logging.info("new '{}' container id is now: {}".format(self.name, new_id))
        f = open(self.name + '.running_container_id', 'w')
        f.write(new_id)
        f.close()
        
        log = open(self.name + ".container_id_log", "a")
        log.write("{} {}\n".format(datetime.datetime.now().isoformat(), new_id))    
    
    def stop(self):
        running_id = self.running_container_id()
        if running_id:
            c.stop(running_id, timeout=30)
        else:
            logging.info("no known instance running")
    
    def start(self):
        # names cannot be reused :( so we need to generate a new one each time
        new_name = self.name + datetime.datetime.now().strftime("-%Y-%m-%d_%H_%M_%S")
        cmdline = "docker run -d --memory=2g  --name={} {} {} ".format(new_name, self.docker_options, self.image_name)
        logging.info("Starting {} container: {}".format(self.name, cmdline))
        #TODO volumes
        new_id = subprocess.check_output(cmdline, shell=True).strip()
        logging.info('started container %s', new_id)
        if len(new_id) != 64:
            raise Exception("cannot parse output when starting container: {}".format(new_id))
        self._set_running_container_id(new_id)
        logging.debug("waiting 2s for startup")
        sleep(2)
        print("Log:")
        self.logs()
        
    def logs(self):
        print(c.logs(container=self.running_container_id(), stream=False))
        
    def follow_logs(self):
        try:
            for l in (c.logs(container=self.running_container_id(), stream=True, timestamps=True, stdout=True, stderr=True, tail=999)):
                print(l)
        except KeyboardInterrupt:
            sys.exit(0)
    
    def is_running(self):
        containers = c.containers()
        running_container_ids = [container['Id'] for container in containers]
        if self.running_container_id() in running_container_ids:
            return True
        for container in containers:
            if container['Image'] == self.image_name: 
                raise Exception("The container '{}', not managed by kastenwesen.py, is currently running from the same image '{}'. I am assuming this is not what you want. Please stop it yourself and restart it via kastenwesen. See the output of 'docker ps' for more info.".format(container['Id'], self.image_name))
        return False

    
    
    def test(self):
        # check that the container is running
        time.sleep(self._tests.get('sleep_before', 1))
        if not self.is_running():
            return False
        something_tested = False
        for url in self._tests.get('http_urls'):
            something_tested = True
            try:
                t = requests.get(url)
                t.raise_for_status()
            except IOError:
                logging.warn("Test failed for HTTP {}".format(url))
                return False
        for obj in self._tests.get('ports'):
            # obj may be a (host, port) tuple or just a port.
            if isinstance(obj, int):
                obj = ('localhost', obj)
            (host, port) = obj
            something_tested = True
            try:
                socket.create_connection((host, port), timeout=2)
            except IOError:
                logging.warn("Test failed for TCP host {} port {}".format(host, port))
                return False
        if not something_tested:
            logging.warn("no tests defined for container {}, a build error might go unnoticed!")
        return True
            
    def print_status(self):
        print("Running: {}".format(self.is_running()))
        print("Tests: ...")
        print("Tests: {}".format(self.test()))
    #def test(self):
        
        
                                  
loglevel = logging.INFO
if "-v" in sys.argv:
    loglevel = logging.DEBUG
logging.basicConfig(level=loglevel)
d=DockerContainer("webserver", "./webserver/", docker_options="-p 80:80", tests={'sleep_before':2, 'http_urls': ['http://localhost'], 'ports': [80]})

d.print_status()

d.rebuild()

d.stop()

d.print_status()

d.start()

d.print_status()