from copy import deepcopy

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

def merge_dicts(adict, overriding):
    '''Recursively merge two deeply nested dictionaries, preferring
    values from 'overriding' when there are colliding keys'''
    for k,v in overriding.iteritems():
        if isinstance(v, dict):
            merge_dicts(adict.setdefault(k, {}), v)
        else:
            adict[k] = v

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
