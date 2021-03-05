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
import time
from . import settings
from . import utils
import pprint
from requests.exceptions import ConnectionError
from unis.models import Node, Service, Measurement

logger = settings.get_logger('conf')

class ServiceConfigure(object):
    '''
    ServiceConfigure is meant to be a generic class for any service
    which registers itself to, and gets configuration from UNIS. It
    was originally developed for BLiPP, but BLiPP specific features
    should be in the BlippConfigure class which extends
    ServiceConfigure.
    '''
    def __init__(self, initial_config={}, node_id=None, urn=None):
        if not node_id:
            node_id = settings.UNIS_ID
        self.node_id = node_id
        self.urn = urn
        self.config = initial_config

    @property
    def unis(self):
        return self._unis

    def initialize(self):
        while True:
            try:
                self._unis = utils.get_unis(self.config['properties']['configurations']['unis_url'])
                r = self._setup_node(self.node_id)
                return self._setup_service()
            except ConnectionError:
                logger.warn(f"Failed to connect to {self.config['properties']['configurations']['unis_url']}")
                time.sleep(int(self.config['properties']['configurations']['unis_poll_interval']))

    def refresh(self):
        self.service.touch()
        return int(self.config['properties']['configurations']['unis_poll_interval'])

    def _setup_node(self, node_id):
        logger.debug("Initializing node...")
        urn = self.urn or settings.HOST_URN
        self.node = self.unis.nodes.first_where({'id': node_id}) or self.unis.nodes.first_where({'urn': urn})
        if not self.node:
            logger.warn("No node found, rebuilding")
            self.node = self.unis.insert(Node({'id': node_id, 'name': settings.HOSTNAME, 'urn': urn}), commit=True)
        self.node_id = self.node.id
        self.config["runningOn"] = self.node

    def _setup_service(self):
        logger.debug("Initializing service...")
        logger.debug(pprint.pformat(self.config))
        s = self.unis.services.first_where({'id': self.config.get('id', "_sentinal")}) or \
            self.unis.services.first_where({'runningOn': self.config['runningOn'],
                                            'name': self.config.get('name', None)})
        if s is None:
            logger.warn("No service found, rebuilding")
            s = self.unis.insert(Service(self.config), commit=True)
        [setattr(s, k, v) for k,v in self.config.items()]
        self.service = s

    def get(self, key, default=None):
        return getattr(self.service, key, default)

    def __getitem__(self, key):
        '''
        This allows an object which is an instance of this class to behave
        like a dictionary when queried with [] syntax
        '''
        try: return getattr(self.service, key)
        except AttributeError as exp: raise KeyError(key) from exp
