from charmhelpers.core import hookenv
from charmhelpers.core import host 

import configparser

def modify_config(section,setting,value):
    ''' modify the config file for couchpotato
    settings should be an input which is an interable of 3 entry tuples in the form:
    (section,config,value)'''
    config = hookenv.config()
    filePath = '/home/{}/.couchpotato/settings.conf'.format(config['couch-user']) 
    configFile = configparser.ConfigParser()
    configFile.read(filePath)
    configFile[section][setting] = value
    with open(filePath,'w') as openFile:
        configFile.write(openFile)

def set_host(hostname):
    modify_config("core","host",hostname)
    hookenv.log("Couch core hostname modified","INFO")

def set_port(port):
    modify_config("core","port",str(port))
    hookenv.log("Couch core port modified","INFO")

def set_indexers(status):
    if status:
        modify_config("newznab","enabled","1")
    else:
        modify_config("newznab","enabled","0")
    hookenv.log("Indexers set to {}".format(status),'INFO')
