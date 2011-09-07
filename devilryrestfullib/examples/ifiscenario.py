from devilryrestfullib import (login,
                               RestfulFactory,
                               RestfulError,
                               HttpResponseNotFound,
                               HttpResponseBadRequest,
                               HttpResponseUnauthorized,
                               HttpResponseForbidden,
                               JsonDecodeError)
from uiodata import subjects

# may be something like http://devilry.myorganzation.com/some/subpath/ in production
devilry_url = 'http://localhost:8000'

# Log in
# - login url may be somthing else if devilry does not handle the login,
#   however this example assumes that devilry is used for login, and the devilry
#   login form is at /authenticate/login
login_url = '{0}/authenticate/login'.format(devilry_url)
logincookie = login(login_url, username='grandma', password='test')

# Create proxy classes which makes it natural to program against the
# RESTful interface using python.
restful_factory = RestfulFactory(devilry_url)
SimplifiedNode = restful_factory.make("/administrator/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("/administrator/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("/administrator/restfulsimplifiedperiod/")
SimplifiedAssignment = restful_factory.make("/administrator/restfulsimplifiedassignment/")
SimplifiedAssignmentGroup = restful_factory.make("/administrator/restfulsimplifiedassignmentgroup/")

uio = {}
matnat = {}
ifi = {}


def all_search():
    """Searches through Node, Subject and Period"""

    print 'Every node in the system:'
    for node in SimplifiedNode.search(logincookie)['items']:
        print '  ', node['short_name'], ':', node['long_name']

    print 'Every subject in the system, ordered _descending_ by short_name:'
    for subject in SimplifiedSubject.search(logincookie, orderby=['-short_name'])['items']:
        print '  ', subject['short_name'], ':', subject['long_name']

    print 'Every Period in the system'
    for period in SimplifiedPeriod.search(logincookie)['items']:
        print '  ', period['short_name'], ':', period['long_name']


def create_uio_matnat_ifi_nodes():
    """Creates Nodes for UiO

    uio is the topmost Node
    matnat is one below uio
    ifi is on the bottom of the Node-hierarchy

    """

    print "CREATE UIO/MATNAT/IFI"
    global uio, matnat, ifi
    uio = SimplifiedNode.create(logincookie, short_name='uio', long_name='Universitetet i Oslo', parentnode=None)
    matnat = SimplifiedNode.create(logincookie, short_name='matnat', long_name='Matematisk Naturvitenskapelig Fakultet', parentnode=uio['id'])
    ifi = SimplifiedNode.create(logincookie, short_name='ifi', long_name='Institutt for informatikk', parentnode=matnat['id'])

def create_subjects_and_period():
    """Creates subjects from a list of IFI-subjects

    Adds h2011 period to each of the subjects
    """

    print "CREATE SUBJECTS"
    for subject in subjects:
        item = SimplifiedSubject.create(logincookie, short_name=subject['short_name'], long_name=subject['long_name'], parentnode=ifi['id'])
        SimplifiedPeriod.create(logincookie, short_name='h2011',
                                long_name='H2011',
                                parentnode=item['id'],
                                start_time='2011-08-01 00:00:01',
                                end_time='2011-12-01 15:00:00')

def search_with_filtering():
    """Creates searching with given filters

    long_name contains
        20 Studiepoeng
        10 Studiepoeng

    """

    print "SEARCH WITH FILTERING"

    studp20 = [{'field':"long_name", 'comp':"icontains", 'value':"20 Studiepoeng"}]
    studp10 = [{'field':"long_name", 'comp':"icontains", 'value':"10 Studiepoeng"}]

    print "Filter long_name contains 20 studiepoeng"
    for subject in SimplifiedSubject.search(logincookie, orderby=['-short_name'],
                                            filters=studp20)['items']:
        print '  ', subject['short_name'], ':', subject['long_name']

    print "Filter long_name contains 10 studiepoeng"
    for subject in SimplifiedSubject.search(logincookie, orderby=['-short_name'],
                                            filters=studp10)['items']:
        print '  ', subject['short_name'], ':', subject['long_name']

def delete_uio():
    SimplifiedNode.delete(logincookie, uio['id'])

if __name__ == '__main__':
    create_uio_matnat_ifi_nodes()
    create_subjects_and_period()
    search_with_filtering()
    delete_uio()


