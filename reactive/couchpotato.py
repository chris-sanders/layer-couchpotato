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
    hookenv.status_set('maintenance','creating user')
    host.adduser(cp.user,password="",shell='/bin/False',home_dir=cp.home_dir)
    hookenv.status_set('maintenance','installing dependencies')
    fetch.apt_update()
    fetch.apt_install(['git','python2.7','python-openssl','python-lxml'])
    
    hookenv.status_set('maintenance','cloning repository')
    if os.path.isdir(cp.install_dir):
        shutil.rmtree(cp.install_dir) 
    subprocess.check_call(["git clone https://github.com/CouchPotato/CouchPotatoServer.git " + cp.install_dir],shell=True)
    host.chownr(cp.home_dir,owner=cp.user,group=cp.user)
    context = {'couchpath':cp.executable,
               'couchuser':cp.user}
    templating.render(cp.service_name,'/etc/systemd/system/{}'.format(cp.service_name),context) 
    cp.enable()
    hookenv.open_port(cp.charm_config['port'],'TCP')
    set_state('couchpotato.installed')
    hookenv.status_set('maintenance','installation complete')

@when('couchpotato.installed')
@when_not('couchpotato.configured')
def setup_config():
    hookenv.status_set('maintenance','configuring')
    backups = './backups'
    if cp.charm_config['restore-config']:
        try:
            os.mkdir(backups)
        except OSError as e:
            if e.errno is 17:
              pass
        backup_file = hookenv.resource_get('couchconfig')
        if backup_file:
            with tarfile.open(backup_file,'r:gz') as inFile:
                inFile.extractall(cp.config_dir)
            host.chownr(cp.home_dir,owner=cp.user,group=cp.user)
            cp.reload_config() 
            cp.set_indexers(False)
        else:
            hookenv.log("Add couchconfig resource, see juju attach or disable restore-config",'ERROR')
            status_set('blocked','Waiting on couchconfig resource')
            return
    else:
        cp.start()
        while not Path(cp.settings_file).is_file():
            time.sleep(1)
        cp.stop()
        cp.reload_config()
    cp.set_host(socket.getfqdn()) # This could use the config parameter and not require checking
    cp.set_port()
    cp.save_config()
    cp.start()
    hookenv.status_set('active','')
    set_state('couchpotato.configured')
