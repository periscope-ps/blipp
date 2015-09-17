#!/bin/bash

USER=blipp
HOME=/var/lib/blipp
PETC=/etc/periscope
SHARE=/usr/share/periscope
LOG=/var/log/blippd.log

useradd -r ${USER} -d ${HOME}
touch ${LOG}
chown ${USER} ${LOG}
cp ${SHARE}/blippd.conf ${PETC}/
cp ${SHARE}/blippd.service /etc/systemd/system/
cp ${SHARE}/blippd.opts /etc/sysconfig/blippd
