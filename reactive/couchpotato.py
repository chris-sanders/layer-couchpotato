from charms.reactive import when, when_all, when_not, set_state
from charmhelpers import fetch
from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core import templating

import os
import subprocess
import shutil
import random
import string

@when_not('couchpotato.installed')
def install_couchpotato():
    config = hookenv.config()
    hookenv.status_set('maintenance','creating user')
    host.adduser(config['couch-user'],password=r''''''.join([random.choice(string.printable) for _ in range(random.randint(8, 12)) if _ != '\\']),shell='/bin/False',home_dir='/home/{}'.format(config['couch-user']))
    hookenv.status_set('maintenance','installing dependencies')
    fetch.apt_update()
    fetch.apt_install(['git','python2.7','python-openssl','python-lxml'])
    
    hookenv.status_set('maintenance','cloning repository')
    subprocess.check_call(["git clone https://github.com/CouchPotato/CouchPotatoServer.git /home/{}/CouchPotatoServer".format(config['couch-user'])],shell=True)
    host.chownr('/home/{}'.format(config['couch-user']),owner=config['couch-user'],group=config['couch-user'])
    context = {'couchpath':'/home/{}/CouchPotatoServer/CouchPotato.py'.format(config['couch-user']),
               'couchuser':config['couch-user']}
    templating.render('couchpotato.service','/etc/systemd/system/couchpotato.service',context) 
    #os.chmod('/home/{}'.format(['couch-user']),0o600)
    # TODO: Restore prevoius config
    # TODO: Modify the config file to set port
    subprocess.check_call('systemctl enable couchpotato.service',shell=True)
    host.service_start('couchpotato.service')
    hookenv.open_port(config['port'],'TCP')
    set_state('couchpotato.installed')
    hookenv.status_set('active','')
