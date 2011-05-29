import urllib2
import json

from login import login
from utils import dict_to_http_querystring

cookiepath = 'logincookie.txt'

# Login
logincookie = login('http://localhost:8000/ui/login',
        username='examiner0', password='test')
open(cookiepath, 'wb').write(logincookie)


# Create url
queryparams = dict(limit=4, start=2)
querystring = dict_to_http_querystring(queryparams)
url = "http://localhost:8000/restful/examiner/assignments/"
full_url = "%s?%s" % (url, querystring)

# Fetch data from url
req = urllib2.Request(full_url)
logincookie = open(cookiepath, 'rb').read()
req.add_header('Cookie', logincookie)
data = urllib2.urlopen(req).read()
print data

# Convert json to python
json_data = json.loads(data)
print json_data
for i in json_data['items']:
    print i['short_name']
