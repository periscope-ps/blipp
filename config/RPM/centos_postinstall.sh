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
GROUP=periscope
HOME=/var/lib/blipp
PETC=/etc/periscope
SHARE=/usr/share/periscope
LOGDIR=/var/log/periscope
LOG=${LOGDIR}/blippd.log

/usr/bin/getent group ${GROUP} || /usr/sbin/groupadd -r ${GROUP}
/usr/bin/getent passwd ${USER} || /usr/sbin/useradd -r -d ${HOME} -s /sbin/nologin ${USER}
/usr/sbin/usermod -a -G ${GROUP} ${USER}

if [ ! -d ${HOME} ]; then
    mkdir -p ${HOME}
fi

chown ${USER}:${GROUP} ${HOME}

if [ ! -d ${PETC} ]; then
    mkdir -p ${PETC}
fi

if [ ! -d ${LOGDIR} ]; then
    mkdir -p /var/log/periscope
fi

chgrp ${GROUP} ${PETC}
chgrp ${GROUP} ${LOGDIR}
chmod g+rwxs ${LOGDIR}

touch ${LOG}
chown ${USER}:${GROUP} ${LOG}

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
