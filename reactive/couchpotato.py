from charms.reactive import when, when_all, when_not, set_state
from charmhelpers import fetch
from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core import templating
from pathlib import Path
from libcouch import CouchInfo

import os
import subprocess
import shutil
import random
import string
import tarfile
import libcouch
import socket
import time

cp = CouchInfo()

@when_not('couchpotato.installed')
def install_couchpotato():
    #config = hookenv.config()
    hookenv.status_set('maintenance','creating user')
    #characters = string.ascii_letters + string.digits
    host.adduser(cp.user,password="",shell='/bin/False',home_dir=cp.home_dir)
    #host.adduser(config['couch-user'],password="",shell='/bin/False',home_dir='/home/{}'.format(config['couch-user']))
    hookenv.status_set('maintenance','installing dependencies')
    fetch.apt_update()
    fetch.apt_install(['git','python2.7','python-openssl','python-lxml'])
    
    hookenv.status_set('maintenance','cloning repository')
    #installPath = "/home/{}/CouchPotatoServer".format(config['couch-user'])
    if os.path.isdir(cp.install_dir):
        shutil.rmtree(cp.install_dir) 
    subprocess.check_call(["git clone https://github.com/CouchPotato/CouchPotatoServer.git " + cp.install_dir],shell=True)
    host.chownr(cp.home_dir,owner=cp.user,group=cp.user)
    context = {'couchpath':cp.executable,
               'couchuser':cp.user}
    templating.render(cp.service_name,'/etc/systemd/system/{}'.format(cp.service_name),context) 
    cp.enable()
    #subprocess.check_call('systemctl enable {}'.format(cp.service_name),shell=True)
    hookenv.open_port(cp.charm_config['port'],'TCP')
    set_state('couchpotato.installed')
    hookenv.status_set('maintenance','installation complete')

@when('couchpotato.installed')
@when_not('couchpotato.configured')
def setup_config():
    hookenv.status_set('maintenance','configuring')
    backups = './backups'
    config = hookenv.config()
    if config['restore-config']:
        try:
            os.mkdir(backups)
        except OSError as e:
            if e.errno is 17:
              pass
        backupFile = hookenv.resource_get('couchconfig')
        if backupFile:
            with tarfile.open(backupFile,'r:gz') as inFile:
                inFile.extractall('/home/{}/.couchpotato'.format(config['couch-user']))
            host.chownr('/home/{}'.format(config['couch-user']),owner=config['couch-user'],group=config['couch-user'])
            # TODO: Modify config via library function
            libcouch.set_indexers(False)
            #libcouch.set_host(socket.getfqdn())
            #libcouch.set_port(config['port'])
            #host.service_start('couchpotato.service')
        else:
            hookenv.log("Add couchconfig resource, see juju attach or disable restore-config",'ERROR')
            status_set('blocked','Waiting on sabconfig resource')
            return
    else:
        host.service_start('couchpotato.service')
        configFile = Path('/home/{}/.couchpotato/settings.conf'.format(config['couch-user']))
        while not configFile.is_file():
            time.sleep(1)
        # TODO: Modify config via library function
        host.service_stop('couchpotato.service')
    libcouch.set_host(socket.getfqdn())
    libcouch.set_port(config['port'])
    host.service_start('couchpotato.service') 
    hookenv.status_set('active','')
    set_state('couchpotato.configured')
