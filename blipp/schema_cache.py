import requests
import json

class SchemaCache:
    def __init__(self):
        self.schemas = {}

    def get(self, schema_url):
        if self.schemas.has_key(schema_url):
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
