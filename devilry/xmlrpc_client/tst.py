from cookielib import LWPCookieJar
import urllib2
import os
from urllib import urlencode

cookiepath = 'stuff.cookie.txt'
loginurl = 'http://localhost:8000/ui/login'
cj = LWPCookieJar()
urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
if os.path.isfile(cookiepath):
    cj.load(cookiepath)
    data = urlopener.open('http://localhost:8000/')
    print data.info()
    print data.read()
else:
    data = urlencode({
        #'user': 'espeak',
        #'password':'',
        'username': 'clarabelle',
        'password':'test',
    })

    data = urlopener.open(loginurl, data)
    print data.info()
    print data.read()
cj.save(cookiepath)
