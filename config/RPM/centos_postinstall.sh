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

USER=blipp
HOME=/var/lib/blipp
PETC=/etc/periscope
SHARE=/usr/share/periscope
LOG=/var/log/blippd.log

/usr/bin/getent group ${USER} || /usr/sbin/groupadd -r ${USER}
/usr/bin/getent passwd ${USER} || /usr/sbin/useradd -r -d ${HOME} -s /sbin/nologin -g ${USER} ${USER}

if [ ! -d ${HOME} ]; then
    mkdir ${HOME}
fi

chown ${USER}:${USER} ${HOME}

if [ ! -d ${PETC} ]; then
    mkdir ${PETC}
fi

chown ${USER}:${USER} ${PETC}

touch ${LOG}
chown ${USER}:${USER} ${LOG}

cp ${SHARE}/blippd.conf ${PETC}/
if grep -q -i "release 6" /etc/redhat-release
then
  cp ${SHARE}/blippd /etc/init.d/blippd
  chmod +x /etc/init.d/blippd
  chown root:root /etc/init.d/blippd
  /sbin/chkconfig --add blippd
elif grep -q -i "release 7" /etc/redhat-release
then
  cp ${SHARE}/blippd.service /etc/systemd/system/
  /usr/bin/systemctl daemon-reload
  /usr/bin/systemctl enable blippd
fi

if [ ! -f /etc/sysconfig/blippd ]; then
    cp ${SHARE}/blippd.opts /etc/sysconfig/blippd
fi
