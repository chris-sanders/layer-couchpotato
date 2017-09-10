# Overview

This charm provides [CouchPotato][couchpotato]. CouchPotato is an automatic NZB
downloader for movies written in python.

# Usage

To deploy:

    juju deploy cs:~chris.sanders/couchpotato

This charm implements 
 * [interface:reverseproxy][interface-reverseproxy] intended for use with the 
   [HAProxy Charm][charm-haproxy]. This should be used if remote access is required 
   to enable TLS encryption. 
 * [interface:usenetdownloader][interface-usenetdownloader] intended for use
   with the [Sabnzbd Charm][charm-sabnzbd]. A downloader is required for
   downloading and unpacking NZBs. 

## Known Limitations and Issues

This charm is under development, several other usecases/features are still under
consideration. Merge requests are certinaly appreciated, some examples of
current limitations include.

 * Scale out usage is not intended, I'm not even sure what use it would be.
 * Unit/Functional testing is not yet implemented

# Configuration
You will most likely want to use a bundle to set options during deployment. 

See the full list of configuration options below. This will detail some of the
options that are worth highlighting.

 - restore-config: Combined with a resource allows restoring a previous
   configuration. Advanced users can use this to migrate from non-charmed
   couchpotato. The settings.conf and database folder need to be provided in a
   tar file.
 - backup-*: The backup options will create a tar file compatible with the above
   restore.
 - proxy-*: The proxy settings allow configuration of the reverseproxy interface
   that will be registered during relation.
 - hostname will allow you to customize the hostname, be aware that
   doing this can cause multiple hosts to have the same hostname if you scale
   out the number of units. Setting hostname to "$UNIT" will set the hostname to
   the juju unit id. Note scaling out is not supported, tested, or useful.

# Contact Information

## Upstream Project Information

  - Code: https://github.com/chris-sanders/layer-couchpotato 
  - Bug tracking: https://github.com/chris-sanders/layer-couchpotato/issues
  - Contact information: sanders.chris@gmail.com

[couchpotato]: https://couchpota.to/ 
[charm-haproxy]: https://jujucharms.com/u/chris.sanders/haproxy
[charm-sabnzbd]: https://jujucharms.com/u/chris.sanders/sabnzbd
[interface-reverseproxy]: https://github.com/chris-sanders/interface-reverseproxy
[interface-usenetdownloader]: https://github.com/chris-sanders/interface-usenet-downloader

