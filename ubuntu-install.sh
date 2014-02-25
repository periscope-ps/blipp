#!/bin/bash
#
# Self-extracting bash script that installs blipp
#
# create self extracting tarball like this (from parent dir): 
# 'tar zc blipp | cat blipp/ubuntu-install.sh - > blipp.sh'
# Supports: Debian based distributions
# Depends: python 2.6

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

SKIP=`awk '/^__TARFILE_FOLLOWS__/ { print NR + 1; exit 0; }' $0`
THIS=`pwd`/$0
tail -n +$SKIP $THIS | tar -xz

DIR=periscope-ps-blipp
ETC=/usr/local/etc

apt-get -y install python-setuptools python-dev python-zmq python-dateutil libnl-dev
cd ${DIR}
python ./setup.py install 

install -D config/blipp_default.json ${ETC}

exit 0

__TARFILE_FOLLOWS__
