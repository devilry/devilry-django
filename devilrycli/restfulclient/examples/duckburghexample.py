from login import login
from devilrycli.restfulclient import RestfulFactory
from errors import (HttpResponseForbidden, HttpResponseBadRequest,
                    HttpResponseUnauthorized, HttpResponseNotFound)


devilry_url = 'http://localhost:8000'
login_url = '{0}/authenticate/login'.format(devilry_url)
logincookie = login(login_url, username='grandma', password='test')

# Create proxy classes which makes it natural to program against the
# RESTful interface using python.
restful_factory = RestfulFactory("http://localhost:8000/")
SimplifiedNode = restful_factory.make("administrator/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("administrator/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("administrator/restfulsimplifiedperiod/")

print 'Every node in the system:'
for node in SimplifiedNode.search(logincookie)['items']:
    print '  ', node['short_name'], ':', node['long_name']

print 'Every subject in the system, ordered _descending_ by short_name:'
for subject in SimplifiedSubject.search(logincookie, orderby=['-short_name'])['items']:
    print '  ', subject['short_name'], ':', subject['long_name']
