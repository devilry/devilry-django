from django.conf import settings


def create_absolute_url(path):
    if path.startswith('http'):
        #from urlparse import urlparse
        #path = urlparse(path).path
        return path
    url = '{domain}{prefix}{path}'.format(domain = settings.DEVILRY_SCHEME_AND_DOMAIN,
                                          prefix = settings.DEVILRY_URLPATH_PREFIX,
                                          path = path)
    return url
