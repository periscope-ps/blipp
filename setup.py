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
#!/usr/bin/env python
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from setuptools import setup

version = "2.0.dev"

setup(
    name="blipp",
    version=version,
    packages=["blipp", "scripts", "blipp.schedules"],
    package_data={},
    author="Matthew Jaffee",
    author_email="matthew.jaffee@gmail.com",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    url="https://github.com/periscope-ps/periscope",
    description="BLiPP: Basic Lightweight Periscope Probes",
    data_files = [("/usr/share/periscope", ["config/blippd.conf",
                                            "config/RPM/blippd",
                                            "config/RPM/blippd.service",
                                            "config/RPM/blippd.opts"])],
    install_requires=[
        "validictory",
        "requests",
        "netlogger>=4.3.0",
        "netifaces",
        "pyzmq",
        "psutil",
        "docopt",
        "python-daemon>=1.5",
        "python-dateutil",
        "unittest2"
    ],
    dependency_links=[
        "http://129.79.244.8/python-ethtool-0.7.tar#egg=ethtool-0.7",
    ],
    entry_points = {
        'console_scripts': [
            'blippd = blipp.blippd:main',
            'blippcmd = scripts.blippcmd:main'
        ]
    },
    options = {'bdist_rpm':{'post_install' : 'config/RPM/centos_postinstall.sh',
                            'post_uninstall' : 'config/RPM/centos_postuninstall.sh'}},
)
