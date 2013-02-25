import http
import json
import settings
import re

logger = settings.get_logger('gemini_client')

class GeminiClient:
    def __init__(self, config, url):
        self.config = config
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
            r = http.make_request(rtype, url, headers, json.dumps(data),
                                  config['ssl_cert'], config['ssl_key'],
                                  config['ssl_cafile'])
        else:
            r = http.make_request(rtype, url, headers, json.dumps(data))
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
        if "geni" in self.config.get("properties", {}):
            geni = post_dict.setdefault(loc, {}).setdefault("geni", {})
            geni.update(self.config["properties"]["geni"])


    def get(self, url, data=None, headers=None):
        return self.do_req('get', url, data, headers)
