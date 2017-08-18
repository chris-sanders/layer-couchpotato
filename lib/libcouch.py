from charmhelpers.core import hookenv
from charmhelpers.core import host 

import configparser
import subprocess
import socket


class CouchInfo:
    def __init__(self):
        self.charm_config = hookenv.config()
        self.user = self.charm_config['couch-user']
        self.home_dir = '/home/{}'.format(self.user)
        self.install_dir = self.home_dir + '/CouchPotatoServer'
        self.executable = self.install_dir + '/CouchPotato.py'
        self.config_dir = self.home_dir + '/.couchpotato'
        self.service_name = 'couchpotato.service'
        self.settings_file = self.home_dir + '/.couchpotato/settings.conf'
        self.couch_config = configparser.ConfigParser()
        self.couch_config.read(self.settings_file)

    def reload_config(self):
        self.couch_config.read(self.settings_file)

    def save_config(self):
        with open(self.settings_file, 'w') as openFile:
            self.couch_config.write(openFile)

    def set_host(self, hostname):
        self.couch_config['core']['host'] = hostname
        hookenv.log("Couchpotato hostname set to {}".format(hostname), "INFO")

    def set_port(self):
        self.couch_config['core']['port'] = str(self.charm_config['port'])
        hookenv.log("Couchpotato port set to {}".format(self.charm_config['port']), "INFO")

    def set_indexers(self, status):
        if status:
            self.couch_config["newznab"]["enabled"] = "1"
        else:
            self.couch_config["newznab"]["enabled"] = "0"
        hookenv.log("Indexers set to {}".format(status), 'INFO')

    def start(self):
        host.service_start(self.service_name)
        hookenv.log("Starting couchpotato", 'INFO')

    def stop(self):
        host.service_stop(self.service_name)
        hookenv.log("Stoping couchpotato", 'INFO')

    def restart(self):
        host.service_restart(self.service_name)
        hookenv.log("Restarting couchpotato", 'INFO')

    def enable(self):
        subprocess.check_call('systemctl enable {}'.format(self.service_name), shell=True)
        hookenv.log("Couchpotato service enabled", 'INFO')

    def configure_sabnzbd(self, host, port, api_key):
        self.couch_config['sabnzbd']['host'] = '{}:{}'.format(host, port)
        self.couch_config['sabnzbd']['api_key'] = api_key
        self.save_config()

    def configure_plex(self, host, port, user=None, passwd=None):
        self.couch_config['plex']['media_server'] = host
        self.couch_config['plex']['host'] = socket.getfqdn()
        if user:
            self.couch_config['plex']['username'] = user
        if passwd:
            self.couch_config['plex']['password'] = passwd
        self.save_config()

    def set_urlbase(self, urlbase):
        self.couch_config['core']['url_base'] = urlbase
        self.save_config()

    def check_port(self):
        self.reload_config()
        hookenv.log('couch_config port: {}'.format(self.couch_config['core']['port']), 'DEBUG')
        hookenv.log(type(self.couch_config['core']['port']), 'DEBUG')
        hookenv.log('charm_port: {}'.format(self.charm_config['port']), 'DEBUG')
        hookenv.log(type(self.charm_config['port']), 'DEBUG')
        if self.couch_config['core']['port'] != str(self.charm_config['port']):
            hookenv.log('Resetting Couch port to match charm, port should not be'
                        'changed via couchpotato', 'WARNING')
            self.set_port()
            self.save_config()

