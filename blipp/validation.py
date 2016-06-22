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
import validictory

def validate_add_defaults(data, schema):
    validictory.validate(data, schema)
    add_defaults(data, schema)

def add_defaults(data, schema):
    # assume data is valide with schema
    if not "properties" in schema:
        return
    for key, inner_schema in schema["properties"].items():
        if not key in data:
            if "default" in inner_schema:
                data[key] = inner_schema["default"]
        elif inner_schema["type"] == "object":
            add_defaults(data[key], inner_schema)
