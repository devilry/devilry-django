"""
Utils that makes testing of ``devilry.rest`` apps easier.
"""

def dummy_urlreverse(restcls, apipath, apiversion, id=None):
    return '{0}-{1}.{2}-{3}'.format(restcls.__name__, apipath, apiversion, id)

def isoformat_datetime(datetimeobj):
    """
    Convert a ``datetime.datetime`` object to the string format expected by
    :func:`.indata.isoformatted_datetime`.
    """
    return datetimeobj.strftime('%Y-%m-%dT%H:%M:%S')
