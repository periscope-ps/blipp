import settings
import pprint
import json
import httplib
from urlparse import urlparse

logger = settings.get_logger('http')

def handle(r):
    text = r.read()
    logger.debug('handle', status=r.status, text=text, reason=r.reason)
    if 200 <= r.status <= 299:
        if text:
            return text
        else:
            return r.status
    elif 400 <= r.status <= 499:
        return None
    else:
        raise Blipp_HTTP_Error(r.status, text)

def make_request(rtype, rurl, headers, data,
                 ssl_cert=None, ssl_key=None, ssl_cafile = None):
    logger.debug('make_request', rtype=rtype, url=rurl, data=pprint.pformat(json.loads(data)))
    o = urlparse(rurl)
    if ssl_cert is not None and ssl_key is not None:
        conn = httplib.HTTPSConnection(o.hostname, o.port, ssl_key, ssl_cert)
    else:
        conn = httplib.HTTPConnection(o.hostname, o.port)

    if rtype.upper()=="GET":
        if headers:
            conn.request("GET", o.path + '?' + o.query, data, headers)
        else:
            conn.request("GET", o.path + '?' + o.query, data)
    else:
        if headers:
            conn.request(rtype.upper(), o.path, data, headers)
        else:
            conn.request(rtype.upper(), o.path, data)
    return handle(conn.getresponse())

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
