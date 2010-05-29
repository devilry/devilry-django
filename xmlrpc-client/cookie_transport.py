import xmlrpclib
from urllib2 import Request
from cookielib import LWPCookieJar
from os.path import isfile


COOKIEFILE = "cookies.txt"


class CookieResponse(object):
    def __init__(self, response):
        self.response = response
    def info(self):
        return self.response


class CookieRequest(object):
    def __init__(self, connection, urltype, host, path):
        self.connection = connection
        self.urltype = urltype
        self.host = host
        self.path = path

    def get_full_url(self):
        return self.urltype + '://' + self.host + self.path

    def get_host(self):
        return self.host

    def get_type(self):
        return self.urltype

    def is_unverifiable(self):
        return False

    def get_origin_req_host(self):
        return 'localhost'

    def has_header(self, header):
        return False

    def add_unredirected_header(self, key, header):
        self.connection.putheader(key, header)


class CookieTransport(xmlrpclib.Transport):

    user_agent = 'devilry-rpc-client (http://devilry.github.com)'

    def __init__(self, SESSION_ID_STRING='sessionid'):
        xmlrpclib.Transport.__init__(self)
        self.mycookies=None
        #self.mysessid="fc1718e8e58d41133fefea184695d02f"
        self.mysessid=None
        self.SESSION_ID_STRING = SESSION_ID_STRING

    def request(self, host, handler, request_body, verbose=0):
        """ issue XML-RPC request """

        # Load cookies from file
        cj = LWPCookieJar()
        if isfile(COOKIEFILE):
            cj.load(COOKIEFILE)

        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)

        # Add cookie headers
        cookie_request = CookieRequest(h, 'http', host, handler)
        cj.add_cookie_header(cookie_request)

        self.send_user_agent(h)
        self.send_content(h, request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
                )

        self.verbose = verbose

        try:
            sock = h._conn.sock
        except AttributeError:
            sock = None

        # Set cookies if any Set-Cookie headers in response
        cookie_response = CookieResponse(headers)
        cj.extract_cookies(cookie_response, cookie_request)
        cj.save(COOKIEFILE)

        return self._parse_response(h.getfile(), sock)
