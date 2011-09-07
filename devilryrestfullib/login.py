import urllib
from urlparse import urlparse
import httplib
from Cookie import SimpleCookie
from devilryclient.utils import findconffolder
from getpass import getpass
from os.path import join, exists
from os import chmod
import stat
import ConfigParser


class LoginError(Exception):
    """Raised on login error"""


def get_session_cookie():
    if exists(join(findconffolder(), 'session')):
        session = open(join(findconffolder(), 'session'), 'r')
        cookieout = session.read()
        session.close()
        return cookieout
    else:
        return login()


def login():

    confdir = findconffolder()
    conf = ConfigParser.ConfigParser()
    conf.read(join(confdir, 'config'))

    # make the url and credentials
    url = join(conf.get('resources', 'url'), 'authenticate/login')

    username = raw_input("Username: ")
    password = getpass("Password: ")

    creds = urllib.urlencode({'username': username, 'password': password})

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
    chmod(join(confdir, 'session'), stat.S_IRUSR | stat.S_IWUSR)

    conf.set('resources', 'user', username)

    with open(join(confdir, 'config'), 'wb') as f:
        conf.write(f)

    return cookieout
