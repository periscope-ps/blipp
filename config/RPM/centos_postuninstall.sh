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

if grep -q -i "release 6" /etc/redhat-release
then
    if [ $1 -eq 0 ]; then
	# disable blipp service only at remove
	/sbin/service blippd stop >/dev/null 2>&1
	/sbin/chkconfig --del blippd
    fi
elif grep -q -i "release 7" /etc/redhat-release
then
    if [ $1 -eq 0 ]; then
        # disable blipp service only at remove
	/sbin/service blippd stop >/dev/null 2>&1
	/usr/bin/systemctl disable blippd
    fi
    systemctl daemon-reload
fi
