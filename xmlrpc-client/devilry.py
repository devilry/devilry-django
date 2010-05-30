#!/usr/bin/env python

from xmlrpclib import ServerProxy, Error
from sys import exit
from cookie_transport import CookieTransport, SafeCookieTransport

# TODO: make sure SESSION_COOKIE_SECURE is enabled by default or something
#       see: http://docs.djangoproject.com/en/dev/topics/http/sessions/#settings




USER_DISABLED = 1
SUCCESSFUL_LOGIN = 2
LOGIN_FAILED = 3

#host = "https://localhost/django/example/xmlrpc/"
#server = ServerProxy(host, transport=SafeCookieTransport())

host = "http://localhost:8000/xmlrpc/"
server = ServerProxy(host, transport=CookieTransport())


try:
    ret = server.login("examiner2", "test")
    if ret == SUCCESSFUL_LOGIN:
        print 'Login successful'
    else:
        print 'Login failed. Reason:'
        if ret == USER_DISABLED:
            print 'Your user is disabled.'
        elif ret == LOGIN_FAILED:
            print 'Invalid username/password.'
        exit(1)

    print server.sum(1, 2)
    #print server.list_assignmentgroups(1)
except Error, v:
    print "ERROR", v
