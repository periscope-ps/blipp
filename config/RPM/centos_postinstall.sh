#!/bin/bash

USER=blipp
HOME=/var/lib/blipp
PETC=/etc/periscope
SHARE=/usr/share/periscope
LOG=/var/log/blippd.log

useradd -r ${USER} -d ${HOME}
if [ ! -d ${HOME} ]; then
    mkdir ${HOME}
fi

chown ${USER}:${USER} ${HOME}

touch ${LOG}
chown ${USER}:${USER} ${LOG}

if grep -q -i "release 6" /etc/redhat-release
then
  cp ${SHARE}/blippd /etc/init.d/blippd
  chmod +x /etc/init.d/blippd
  chown root:root /etc/init.d/blippd
  chkconfig --add blippd
elif grep -q -i "release 7" /etc/redhat-release
  cp ${SHARE}/blippd.conf ${PETC}/
  cp ${SHARE}/blippd.service /etc/systemd/system/
else
  echo "Unsupported system"
fi

if [ ! -f /etc/sysconfig/blippd ]; then
    cp ${SHARE}/blippd.opts /etc/sysconfig/blippd
fi
systemctl daemon-reload
