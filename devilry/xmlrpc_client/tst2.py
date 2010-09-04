from cookielib import LWPCookieJar
import urllib2
import os
from urllib import urlencode

cookiepath = 'stuff.cookie.txt'
loginurl = 'https://devilry.ifi.uio.no/'
cj = LWPCookieJar()
urlopener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#if os.path.isfile(cookiepath):
    #cj.load(cookiepath)
    #data = urlopener.open('https://devilry.ifi.uio.no/')
    #print data.info()
    #print data.read()
#else:
data = urlencode({
    'user': 'espeak',
    'password':'',
})

request = urllib2.Request(loginurl)
try:
    data = urlopener.open(loginurl, data)
except urllib2.HTTPError, e:
    print dir(e)
    print "Retcode: ", e.code
    print "Headers:"
    print e.headers
    print "Info:"
    #print e.info()
    #print request.get_full_url()
    cj.extract_cookies(e, request)
    print cj
    cj.save(cookiepath)
else:
    print data.info()
    print
    print
    print data.read()
#cj.save(cookiepath)
