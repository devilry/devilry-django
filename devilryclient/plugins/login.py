#!/usr/bin/env python

#from devilryclient.restfulclient import login

#getpass module
#username as argument, prompt for password
#create logincookie and save it in .devilry folder

# logincookie = login('http://localhost:8000/authenticate/login',
#         username='grandma', password='test')

import httplib
import urllib
import urllib2
import cookielib
from urlparse import urlparse
from devilryclient import utils
import ConfigParser
from os.path import join, exists
from Cookie import SimpleCookie


class LoginError(Exception):
    """ Raised when login errors occur """


def login():
    # grab the config file
    confdir = utils.findconffolder()
    conf = ConfigParser.ConfigParser()
    conf.read(join(confdir, 'config'))

    if exists(join(confdir, 'session')):
        session = open(join(confdir, 'session'), 'r')
        cookieout = session.read()
        session.close()
        return cookieout

    # make the url and credentials
    url = join(conf.get('URL', 'url'), 'authenticate/login')
    creds = urllib.urlencode({'username': 'grandma', 'password': 'test'})

    parsed_url = urlparse(url)
    host = parsed_url.netloc

    if parsed_url.scheme == "https":
        conn = httplib.HTTPSConnection(host)
    else:
        conn = httplib.HTTPConnection(host)

    response = conn.request('POST', parsed_url.path, creds, {'Content-type': "application/x-www-form-urlencoded"})

    response = conn.getresponse()
    if response.status > 400:
        raise LoginError("Login to %s failed with the following message: %s %s (%s)" % (
                url, response.status, response.reason, response.msg))

    response.read()
    setcookie = response.getheader('Set-Cookie')
    if setcookie == None:
        raise LoginError("Login failed. This is usually because of "
                         "invalid username/password, but might be "
                         "caused by wrong login urlprefix or server errors. "
                         "Technical error message: Login urlprefix did not "
                         "respond with any authorization cookies.")

    cookie = SimpleCookie()
    cookie.load(setcookie)
    cookieout = cookie.output().replace('Set-Cookie: ', '')
    session = open(join(confdir, 'session'), 'w')
    session.write(cookieout)
    session.close()

    return cookieout

if __name__ == '__main__':
    login()
