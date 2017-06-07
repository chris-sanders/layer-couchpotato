from charmhelpers.core import hookenv
from charmhelpers.core import host 

import configparser
import subprocess

class CouchInfo:
    def __init__(self):
        self.charm_config = hookenv.config()
        self.user = self.charm_config['couch-user']
        self.home_dir = '/home/{}'.format(self.user)
        self.install_dir = self.home_dir+'/CouchPotatoServer'
        self.executable = self.install_dir+'/CouchPotato.py'
        self.config_dir = self.home_dir+'/.couchpotato'
        self.service_name = 'couchpotato.service'
        self.settings_file = self.home_dir+'/.couchpotato/settings.conf'
        self.couch_config = configparser.ConfigParser()
        self.couch_config.read(self.settings_file)

    def reload_config(self):
        self.couch_config.read(self.settings_file)

    def save_config(self):
        with open(self.settings_file,'w') as openFile:
            self.couch_config.write(openFile)

    def set_host(self,hostname):
        self.couch_config['core']['host'] = hostname
        hookenv.log("Couchpotato hostname set to {}".format(hostname),"INFO")

    def set_port(self):
        self.couch_config['core']['port'] = str(self.charm_config['port'])
        hookenv.log("Couchpotato port set to {}".format(self.charm_config['port']),"INFO")

    def set_indexers(self,status):
        if status:
            self.couch_config["newznab"]["enabled"] = "1"
        else:
            self.couch_config["newznab"]["enabled"] = "0"
        hookenv.log("Indexers set to {}".format(status),'INFO')

    def start(self):
        host.service_start(self.service_name)
        hookenv.log("Starting couchpotato",'INFO')

    def stop(self):
        host.service_stop(self.service_name)
        hookenv.log("Stoping couchpotato",'INFO')

    def restart(self):
        host.service_restart(self.service_name)
        hookenv.log("Restarting couchpotato",'INFO')

    def enable(self):
        subprocess.check_call('systemctl enable {}'.format(self.service_name),shell=True)
        hookenv.log("Couchpotato service enabled",'INFO')
