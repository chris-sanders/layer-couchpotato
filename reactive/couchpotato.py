from charms.reactive import when, when_all, when_not, set_state
from charmhelpers import fetch
from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core import templating

import os

@when_not('couchpotato.installed')
def install_couchpotato():
    config = hoookenv.config()
    hookenv.status_set('maintenance','creating user')
    host.adduser(config['couch-user'],home_dir='/home/'+config['couch-user'])
    hookenv.status_set('maintenance','installing dependencies')
    fetch.apt_update()
    fetch.apt_install(['git','lxml','pyopenssl'])
    
    hookenv.status_set('maintenance','cloning repository')
    subprocess.check_call(["git clone https://github.com/CouchPotato/CouchPotatoServer.git /home/{}".format(config['couch-user'])],shell=True)
    host.chownr('/home/{}'.format(['couch-user']),user=config['couch-user'],group=config['couch-user'])
    context = {'couchpath':'/home/{}/CouchPotatoServer/CouchPotato.py'.format(config['couch-user']),
               'couchuser':config['couch-user']}
    templating.render('couchpotato.service','/etc/systemd/system/couchpotato.service',context) 
    #os.chmod('/home/{}'.format(['couch-user']),0o600)
    set_state('couchpotato.installed')
    hookenv.status_set('active','')
