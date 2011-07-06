import urllib

def dict_to_http_querystring(dct):
    return '&'.join(['%s=%s' % (k, urllib.quote(str(v)))\
        for k,v in dct.iteritems()])
