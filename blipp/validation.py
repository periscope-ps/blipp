import validictory

def validate_add_defaults(data, schema):
    validictory.validate(data, schema)
    add_defaults(data, schema)

def add_defaults(data, schema):
    # assume data is valide with schema
    if not schema.has_key("properties"):
        return
    for key, inner_schema in schema["properties"].items():
        if not data.has_key(key):
            if inner_schema.has_key("default"):
                data[key] = inner_schema["default"]
        elif inner_schema["type"] == "object":
            add_defaults(data[key], inner_schema)
