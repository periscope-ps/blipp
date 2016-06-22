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
from copy import deepcopy
import re
import struct
import socket

def try__import__(name):
    try:
        ret=__import__(name)
    except ImportError:
        SETTINGS_FILE = "blipp" + "." + name
        try:
            ret=__import__(SETTINGS_FILE)
            ret = getattr(ret, name)
        except ImportError:
            ret=None

    return ret

def blipp_import(name, **kwargs):
    try:
        ret = __import__(name, fromlist=[1])
    except ImportError:
        ret = __import__("blipp." + name, fromlist=[1])
    return ret

def blipp_import_method(method_string):
    mod, dot, method = method_string.rpartition(".")
    mod = blipp_import(mod)
    return mod.__getattribute__(method)

def get_most_recent(resources):
    res_dict = {}
    for res in resources:
        if res['id'] in res_dict:
            if res['ts'] > res_dict[res['id']]['ts']:
                res_dict[res['id']] = res
        else:
            res_dict[res['id']] = res

    res = []
    for href in res_dict:
        res.append(res_dict[href])
    return res

def full_event_types(data, EVENT_TYPES):
    result = {}
    if isinstance(data.itervalues().next(), dict):
        for subject in data.keys():
            subresult = {}
            for k,v in data[subject].iteritems():
                subresult[EVENT_TYPES[k]]=v
            result[subject]=subresult
        return result
    else:
        for k,v in data.iteritems():
            result[EVENT_TYPES[k]]=v
        return result

def remove_old_resources(resource_list):
    """
    Remove resources in a list which have the same id as another resource but an older timestamp
    """
    uniques = []
    ids = set()
    for r in resource_list:
        if r["id"] not in ids:
            uniques.append(r)
            ids.add(r["id"])
    return uniques

def delete_nones(adict):
    '''Recursively delete None (json null) values from a deeply nested
    dictionary'''
    del_keys = []
    for k,v in adict.iteritems():
        if isinstance(v, dict):
            delete_nones(v)
        elif v==None:
            del_keys.append(k)

    for k in del_keys:
        del adict[k]

def merge_dicts(base, overriding):
    '''Recursively merge 'overriding' into base (both nested
    dictionaries), preferring values from 'overriding' when there are
    colliding keys
    '''
    for k,v in overriding.iteritems():
        if isinstance(v, dict):
            merge_dicts(base.setdefault(k, {}), v)
        else:
            base[k] = v

def merge_into(base, defaults):
    '''Recursively merge 'defaults' into base (both nested dictionaries),
    preferring values from 'base' when there are colliding keys
    '''
    for k,v in defaults.items():
        if isinstance(v, dict) and isinstance(base.get(k, None), dict):
            merge_into(base.setdefault(k, {}), v)
        elif not k in base:
            base[k] = v


def reconcile_config(defaults, master):
    ans = deepcopy(defaults)
    for key, val in master.iteritems():
        if not isinstance(val, dict):
            ans[key] = val
        else:
            if key in ans:
                ans[key] = reconcile_config(ans[key], master[key])
            else:
                ans[key] = deepcopy(val)
    return ans

def query_string_from_dict(adict, prefix=""):
    '''Construct a UNIS REST API query string from a dictionary'''
    retstring = ""
    if prefix:
        prefix += "."
    for k,v in adict.items():
        # a hack: UNIS doesn't like queries that have a '$' in the key for some reason
        if "$" in k:
            continue
        if isinstance(v, dict):
            retstring += query_string_from_dict(v, prefix + str(k))
        else:
            if isinstance(v, bool): # bool goes first because isinstance(False, int)==True *sigh*
                retstring += prefix + str(k) + "=boolean:" + str(v).lower() + "&"
            elif isinstance(v, int):
                retstring += prefix + str(k) + "=number:" + str(v) + "&"
            elif isinstance(v, str):
                retstring += prefix + str(k) + "=" + v + "&"
            elif isinstance(v, unicode):
                retstring += prefix + str(k) + "=" + v + "&"
            else:
                print "ATTEMPT TO QUERY ON NON SUPPORTED TYPE:"
                print v

    return retstring

def clean_mac(mac):
    mac = mac.strip().lower().replace(":", "")
    mac = mac.replace(" ", "")
    try:
        return re.search('([0-9a-f]{12})', mac).groups()[0]
    except AttributeError:
        return None

def get_default_gateway_linux():
    """
    Reads the default gateway directly from /proc.
    Returns default interface ip, default interface name
    """
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue
            return socket.inet_ntoa(struct.pack("=L", int(fields[2], 16))),fields[0]
