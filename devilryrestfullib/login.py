import urllib
from urlparse import urlparse
import httplib
from Cookie import SimpleCookie

class LoginError(Exception):
    """ Raised on login errors """

def login(url, **logindata):
    """
    Send a login request to the given login ``url``, and return the login cookie.

    :param url: Url of the login form.
    :param logindata: The required login data (usually username and
        password). With the devilry login form, this is::

            {'user':'myuser', 'password':'mysecret'}

        However it may be something else (on custom login solutions).

    :return: The login cookie as a string on success.
    :throw: LoginError if the login fails.
    """
    parsedurl = urlparse(url)
    host = parsedurl.netloc
    if parsedurl.scheme == "https":
        conn = httplib.HTTPSConnection(host)
    else:
        conn = httplib.HTTPConnection(host)
    #conn.set_debuglevel(1)
    conn.request("POST", parsedurl.path, urllib.urlencode(logindata),
        headers = {
            "Content-type": "application/x-www-form-urlencoded"})
    response = conn.getresponse()
    if response.status < 400:
        data = response.read()
        setcookie = response.getheader("Set-Cookie")
        if setcookie == None:
            raise LoginError("Login failed. This is usually because of "
                    "invalid username/password, but might be "
                    "caused by wrong login urlprefix or server errors. "
                    "Technical error message: Login urlprefix did not "
                    "respond with any authorization cookies.")
        else:
            cookie = SimpleCookie()
            cookie.load(setcookie)
            cookieout = cookie.output().replace("Set-Cookie: ", "")
            cookieout = cookieout.replace('\r', '').replace('\n', '; ')
            return cookieout
    else:
        raise LoginError("Login to %s failed with the following message: %s %s (%s)" % (
                url, response.status, response.reason, response.msg))
