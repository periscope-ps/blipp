#!/bin/bash

USER=blipp
HOME=/var/lib/blipp
PETC=/etc/periscope
SHARE=/usr/share/periscope
LOG=/var/log/blippd.log

if grep -q -i "release 6" /etc/redhat-release
then
    chkconfig --del blippd
    rm -f /etc/init.d/blippd
elif grep -q -i "release 7" /etc/redhat-release
then
    if [ "$1" = "0" ]; then
        # Perform tasks to prepare for the uninstallation
        systemctl disable blippd
        rm -f /etc/systemd/system/blippd.service
    fi
    systemctl daemon-reload
fi

service blippd stop
userdel blipp
