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
import requests
from . import settings
import pprint
import json

logger = settings.get_logger('http')

def handle(resp):
    logger.debug('handle', status=resp.status_code, text=resp.text)
    if 200 <= resp.status_code <= 299:
        if resp.text:
            return resp.text
        else:
            return resp.status_code
    elif 400 <= resp.status_code <= 499:
        return None
    else:
        raise Blipp_HTTP_Error(resp.status_code, resp.text)

def make_request(rtype, rurl, headers, data,
                 ssl_cert=None, ssl_key=None, ssl_cafile=None):
    if not ssl_cafile:
        ssl_cafile = False
    logger.debug('make_request', rtype=rtype, url=rurl, data=pprint.pformat(json.loads(data)))
    return handle(requests.request(rtype, rurl, headers=headers, data=data,
                                   cert=(ssl_cert, ssl_key), verify=ssl_cafile))

def get(get_url, data=None, headers=None,
        ssl_cert=None, ssl_key=None, ssl_cafile = None):
    return make_request('get', get_url, headers, data, ssl_cert, ssl_key, ssl_cafile)

def post(post_url, data=None, headers=None,
         ssl_cert=None, ssl_key=None, ssl_cafile = None):
    return make_request('post', post_url, headers, data, ssl_cert, ssl_key, ssl_cafile)

def delete(delete_url, data=None, headers=None,
           ssl_cert=None, ssl_key=None, ssl_cafile = None):
    return make_request('delete', delete_url, headers, data, ssl_cert, ssl_key, ssl_cafile)


class Blipp_HTTP_Error(Exception):
    def __init__(self, code, text):
        self.code = code
        self.text = text
    def __str__(self):
        return "BLiPP Error - Response code: " + str(self.code) + " Message: " + str(self.text)
