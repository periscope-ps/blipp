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

cp ${SHARE}/blippd.conf ${PETC}/
cp ${SHARE}/blippd.service /etc/systemd/system/

if [ ! -f /etc/sysconfig/blippd ]; then
    cp ${SHARE}/blippd.opts /etc/sysconfig/blippd
fi
systemctl daemon-reload
