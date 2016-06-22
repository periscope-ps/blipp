# =============================================================================
#  periscope-ps (blipp)
#
#  Copyright (c) 2013-2016, Trustees of Indiana University,
#  All rights reserved.
#
#  This software may be modified and distributed under the terms of the BSD
#  license.  See the COPYING file for details.
#
#  This software was created at the Indiana University Center for Research in
#  Extreme Scale Technologies (CREST).
# =============================================================================
#!/bin/bash
#
# Self-extracting bash script that installs blipp
#
# create self extracting tarball like this (from parent dir): 
# 'tar zc blipp | cat blipp/fedora-install.sh - > blipp.sh'
# Supports: Debian based distributions
# Depends: python 2.6

if [ "$(id -u)" != "0" ]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

SKIP=`awk '/^__TARFILE_FOLLOWS__/ { print NR + 1; exit 0; }' $0`
THIS=`pwd`/$0
tail -n +$SKIP $THIS | tar -xz

# Installation steps for LAMP Toolkit
DIR=blipp
ETC=/usr/local/etc

yum -y install python-setuptools python-dateutil libnl-devel
cd ${DIR}
python ./setup.py install 

install -D config/blipp_default.json ${ETC}

exit 0

__TARFILE_FOLLOWS__
