from charms.reactive import when, when_all, when_not, when_file_changed, set_state
from charmhelpers import fetch
from charmhelpers.core import host
from charmhelpers.core import hookenv
from charmhelpers.core import templating
from pathlib import Path
from libcouch import CouchInfo

import os
import subprocess
import shutil
import tarfile
import socket
import time

cp = CouchInfo()


@when_not('couchpotato.installed')
def install_couchpotato():
    hookenv.status_set('maintenance', 'creating user')
    host.adduser(cp.user, password="", shell='/bin/False', home_dir=cp.home_dir)
    hookenv.status_set('maintenance', 'installing dependencies')
    fetch.apt_update()
    fetch.apt_install(['git', 'python2.7', 'python-openssl', 'python-lxml'])

    hookenv.status_set('maintenance', 'cloning repository')
    if os.path.isdir(cp.install_dir):
        shutil.rmtree(cp.install_dir)
    subprocess.check_call(["git clone https://github.com/CouchPotato/CouchPotatoServer.git " + cp.install_dir], shell=True)
    host.chownr(cp.home_dir, owner=cp.user, group=cp.user)
    context = {'couchpath': cp.executable,
               'couchuser': cp.user}
    templating.render(cp.service_name, '/etc/systemd/system/{}'.format(cp.service_name), context)
    cp.enable()
    hookenv.open_port(cp.charm_config['port'], 'TCP')
    set_state('couchpotato.installed')
    hookenv.status_set('maintenance', 'installation complete')


@when('couchpotato.installed')
@when_not('couchpotato.configured')
def setup_config():
    hookenv.status_set('maintenance', 'configuring')
    backups = './backups'
    if cp.charm_config['restore-config']:
        try:
            os.mkdir(backups)
        except OSError as e:
            if e.errno is 17:
                pass
        backup_file = hookenv.resource_get('couchconfig')
        if backup_file:
            with tarfile.open(backup_file, 'r:gz') as inFile:
                inFile.extractall(cp.config_dir)
            host.chownr(cp.home_dir, owner=cp.user, group=cp.user)
            cp.reload_config()
            cp.set_indexers(False)
        else:
            hookenv.log("Add couchconfig resource, see juju attach or disable restore-config", 'ERROR')
            hookenv.status_set('blocked', 'Waiting on couchconfig resource')
            return
    else:
        cp.start()
        while not Path(cp.settings_file).is_file():
            time.sleep(1)
        cp.stop()
        cp.reload_config()
    cp.set_host(socket.getfqdn())  # This could use the config parameter and not require checking
    cp.set_port()
    cp.save_config()
    cp.start()
    hookenv.status_set('active', '')
    set_state('couchpotato.configured')


@when_not('usenet-downloader.configured')
@when_all('usenet-downloader.triggered', 'usenet-downloader.available', 'couchpotato.configured')
def configure_downloader(usenetdownloader, *args):
    hookenv.log("Setting up sabnzbd relation", "INFO")
    cp.stop()
    cp.configure_sabnzbd(host=usenetdownloader.hostname(), port=usenetdownloader.port(), api_key=usenetdownloader.apikey())
    cp.start()
    usenetdownloader.configured()


@when_not('plex-info.configured')
@when_all('plex-info.triggered', 'plex-info.available', 'couchpotato.configured')
def configure_plex(plexinfo, *args):
    hookenv.log("Setting up plex notification", "INFO")
    cp.stop()
    cp.configure_plex(host=plexinfo.hostname(), port=plexinfo.port(), user=plexinfo.user(), passwd=plexinfo.passwd())
    cp.start()
    plexinfo.configured()


@when_all('reverseproxy.triggered', 'reverseproxy.ready')
@when_not('reverseproxy.configured', 'reverseproxy.departed')
def configure_reverseproxy(reverseproxy, *args):
    # TODO: retrigger if charm or couch config change
    hookenv.log("Setting up reverseproxy", "INFO")
    proxy_info = {'urlbase': cp.charm_config['proxy-url'],
                  'subdomain': cp.charm_config['proxy-domain'],
                  'group_id': cp.charm_config['proxy-group'],
                  'external_port': cp.charm_config['proxy-port'],
                  'internal_host': socket.getfqdn(),
                  'internal_port': cp.charm_config['port']
                  }
    reverseproxy.configure(proxy_info)
    cp.set_urlbase(proxy_info['urlbase'])
    cp.restart()


@when_all('reverseproxy.triggered', 'reverseproxy.departed')
def remove_urlbase(reverseproxy, *args):
    hookenv.log("Removing reverseproxy configuration", "INFO")
    cp.set_urlbase('')
    cp.restart()


@when('config.changed.port')
def update_port():
    # During install settings start at 'None' and you can't close None/TCP
    if cp.charm_config.previous('port') is not None:
        hookenv.log('Closing port: {}'.format(cp.charm_config.previous('port')), "INFO")
        hookenv.close_port(cp.charm_config.previous('port'))
        hookenv.log('Opening port: {}'.format(cp.charm_config['port']), "INFO")
        hookenv.open_port(cp.charm_config['port'])
        cp.set_port()
        cp.save_config()


@when_file_changed(cp.settings_file)
def config_file_changed():
    cp.check_port()
