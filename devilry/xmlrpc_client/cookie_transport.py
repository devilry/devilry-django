import xmlrpclib
from cookielib import LWPCookieJar
import os
import stat


class _CookieResponse(object):
    def __init__(self, response):
        self.response = response
    def info(self):
        return self.response


class _CookieRequest(object):
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


class CookieTransportMixin(object):

    user_agent = 'devilry-rpc-client (http://devilry.github.com)'
    urltype = 'http'

    def __init__(self, cookiefile):
        """
        :param cookierfile:
            Path to a file where cookies are stored. This file is chmodded
            so only the current user might access it on posix-systems.
        """
        self.cookiefile = cookiefile
        xmlrpclib.Transport.__init__(self)

    def request(self, host, handler, request_body, verbose=0):
        """ issue XML-RPC request """

        # Load cookies from file
        cj = LWPCookieJar()
        if os.path.isfile(self.cookiefile):
            cj.load(self.cookiefile)

        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        self.send_request(h, handler, request_body)
        self.send_host(h, host)

        # Add cookie headers
        cookie_request = _CookieRequest(h, 'http', host, handler)
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
        cookie_response = _CookieResponse(headers)
        cj.extract_cookies(cookie_response, cookie_request)
        cj.save(self.cookiefile)
        if os.name == 'posix':
            os.chmod(self.cookiefile, stat.S_IWUSR|stat.S_IRUSR)

        return self._parse_response(h.getfile(), sock)


class CookieTransport(CookieTransportMixin, xmlrpclib.Transport):
    """ Unprotected HTTP XMLRPC transport with cookie support. """
    def __init__(self, cookiefile, use_datetime=True):
        """
        :param cookiefile:
            Path to a file where cookies are stored. Cookies are stored
            using cookielib.LWPCookieJar, so they are easy to read.
        :param use_datetime:
            Convert date into ``datetime.datetime`` objects? Defaults to
            ``True``.
        """
        CookieTransportMixin.__init__(self, cookiefile)
        xmlrpclib.Transport.__init__(self, use_datetime=use_datetime)


class SafeCookieTransport(CookieTransportMixin, xmlrpclib.SafeTransport):
    """ Unprotected HTTP XMLRPC transport with cookie support. """
    urltype = 'https'

    def __init__(self, cookiefile, use_datetime=True):
        """
        :param cookiefile:
            Path to a file where cookies are stored. Cookies are stored
            using cookielib.LWPCookieJar, so they are easy to read.
        :param use_datetime:
            Convert date into ``datetime.datetime`` objects? Defaults to
            ``True``.
        """
        CookieTransportMixin.__init__(self, cookiefile)
        xmlrpclib.SafeTransport.__init__(self, use_datetime=use_datetime)
