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
import http
import json
import settings
import re
from requests.exceptions import ConnectionError

logger = settings.get_logger('periscope_client')

class PeriscopeClient:
    def __init__(self, service_entry, url):
        self.service_entry = service_entry
        self.config = service_entry["properties"]["configurations"]
        self.url = url

    def do_req(self, rtype, url, data=None, headers=None):
        config = self.config
        url, schema, dheaders = self._url_schema_headers(url)
        headers = dheaders if not headers else headers
        if isinstance(data, dict):
            if schema:
                data.setdefault('$schema', schema)
            if rtype=='post' or rtype=='put':
                loc = "parameters" if url.count('/metadata') else "properties"
                self._add_gemini_auth(data, loc)
        if config.get("use_ssl", None):
            try:
                r = http.make_request(rtype, url, headers, json.dumps(data),
                                      config.get('ssl_cert', None), config.get('ssl_key', None),
                                      config['ssl_cafile'])
            except Exception as e:
                if isinstance(e, ConnectionError):
                    raise ConnectionError()
                
                logger.info("do_req", msg="Could not reach %s" % url)
                return None
        else:
            try:
                r = http.make_request(rtype, url, headers, json.dumps(data))
            except Exception as e:
                if isinstance(e, ConnectionError):
                    raise ConnectionError()
                
                logger.info("do_req", msg="Could not reach %s" % url)
                return None
        try:
            return json.loads(r)
        except ValueError:
            return r
        except TypeError:
            return r

    def _url_schema_headers(self, url):
        if re.search('^https?://', url):
            m = re.search('^(https?://[^/]*)(/.*)', url)
            urlpref = m.groups()[0]
            url = m.groups()[1]
        else:
            urlpref = self.url
        url = '/' + url if not url[0]=='/' else url
        url = url[:-1] if url[-1]=='/' else url
        try:
            if '?' in url:
                schema = settings.SCHEMAS[url.split('/')[1][:url.find('?')-1]]
            else:
                schema = settings.SCHEMAS[url.split('/')[1]]
        except KeyError:
            schema = ""
        headers = {'content-type':
                          'application/perfsonar+json profile=' + schema,
                          'accept':settings.MIME['PSJSON']}
        if not schema:
            headers=None
        url = urlpref + url
        return url, schema, headers

    def _add_gemini_auth(self, post_dict, loc="properties"):
        if "geni" in self.service_entry.get("properties", {}):
            geni = post_dict.setdefault(loc, {}).setdefault("geni", {})
            geni.update(self.service_entry["properties"]["geni"])


    def get(self, url, data=None, headers=None):
        return self.do_req('get', url, data, headers)
