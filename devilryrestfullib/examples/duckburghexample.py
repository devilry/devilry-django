from devilryrestfullib import (login,
                               RestfulFactory,
                               RestfulError,
                               HttpResponseNotFound,
                               HttpResponseBadRequest,
                               HttpResponseUnauthorized,
                               HttpResponseForbidden,
                               JsonDecodeError)


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


""" ####################################################
                    SEARCH / GET
#################################################### """

def all_search():
    print 'Every node in the system:'
    for node in SimplifiedNode.search(logincookie)['items']:
        print '  ', node['short_name'], ':', node['long_name']

    print 'Every subject in the system, ordered _descending_ by short_name:'
    for subject in SimplifiedSubject.search(logincookie, orderby=['-short_name'])['items']:
        print '  ', subject['short_name'], ':', subject['long_name']

    print 'Every Period in the system'
    for period in SimplifiedPeriod.search(logincookie)['items']:
        print '  ', period['short_name'], ':', period['long_name']

    print 'Every Assignment in the system'
    for assignment in SimplifiedAssignment.search(logincookie)['items']:
        print '  ', assignment['short_name'], ':', assignment['long_name']

    # print 'Every Assignment in the system'
    # for assignmentgroup in SimplifiedAssignmentGroup.search(logincookie)['items']:
        # print '  ', assignmentgroup['status'], ':', assignmentgroup['is_open']


""" ####################################################
                    CREATE / POST
#################################################### """
print "System Status - Initial"
all_search()


print "Create a new Node with no parentnode - Donald Duck University"
donald = SimplifiedNode.create(logincookie, short_name='donald',
                               long_name='Donald Duck University',
                               parentnode=None)

print "Create a new Subject mac1110"
mac1110 = SimplifiedSubject.create(logincookie, short_name='mac1110',
                                   long_name='Introduction in how to maintain a nearly bursting Money Bin',
                                   parentnode=donald['id'])

print "Create a new Period in mac1110"
mac1110v2011 = SimplifiedPeriod.create(logincookie, short_name='v2011',
                                       long_name='V2011',
                                       parentnode=mac1110['id'],
                                       start_time='2011-01-01 00:00:01',
                                       end_time='2011-06-01 15:00:00')

print "System Status - After CREATE/POST"
all_search()


""" ####################################################
                    UPDATE / PUT
#################################################### """


print "Change information about Donald Duck University"
gladgander = SimplifiedNode.update(logincookie, donald['id'],
                                   short_name='gander',
                                   long_name='Gladstone Gander University')

print "Redefine mac1110"
mac5110 = SimplifiedSubject.update(logincookie, mac1110['id'],
                                   short_name='mac5110',
                                   long_name='Advanced Money Swimming',
                                   parentnode=gladgander['id'])

print "System Status - After UPDATE/PUT"
all_search()

""" ####################################################
                    DELETE / DELETE
#################################################### """


print "Delete Period"
SimplifiedPeriod.delete(logincookie, mac1110v2011['id'])

print "Delete Gladstone Ganders university"
SimplifiedNode.delete(logincookie, gladgander['id'])

print "System Status - After DELETE/DELETE"
all_search()



