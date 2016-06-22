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
import json

class SchemaCache:
    def __init__(self):
        self.schemas = {}

    def get(self, schema_url):
        if schema_url in self.schemas:
            return self.schemas[schema_url]
        else:
            return self._fetch_schema(schema_url)

    def _fetch_schema(self, schema_url):
        if schema_url.startswith("file://"):
            schema = json.loads(open(schema_url[7:]).read())
        else:
            schema = requests.get(schema_url).json()

        self.schemas[schema_url] = schema
        return schema
