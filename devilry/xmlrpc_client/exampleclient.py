#!/usr/bin/env python

from xmlrpclib import ServerProxy, Error
from cookie_transport import CookieTransport, SafeCookieTransport

USER_DISABLED = 1
LOGIN_FAILED = 2
SUCCESSFUL_LOGIN = 3

## Connect to unprotect server
host = "http://localhost:8000/"
server = ServerProxy(host, transport=CookieTransport('cookies.txt'),
        allow_none=True)

## Connect to SSL-protected server
#host = "https://localhost/django/example/xmlrpc/"
#server = ServerProxy(host, transport=SafeCookieTransport(), allow_none=True)

try:
    ret = server.login("examiner1", "test")
    if ret == SUCCESSFUL_LOGIN:
        print 'Login successful'
    else:
        print 'Login failed. Reason:'
        if ret == USER_DISABLED:
            print 'Your user is disabled.'
        elif ret == LOGIN_FAILED:
            print 'Invalid username/password.'
        raise SystemExit()

    print server.sum(1, 2)
    print server.list_assignmentgroups(1)
except Error, v:
    print "ERROR", v
