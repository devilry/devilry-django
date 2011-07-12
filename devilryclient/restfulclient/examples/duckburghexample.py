from devilryclient.restfulclient import (login,
                                      RestfulFactory,
                                      RestfulError,
                                      HttpResponseNotFound,
                                      HttpResponseBadRequest,
                                      HttpResponseUnauthorized,
                                      HttpResponseForbidden,
                                      JsonDecodeError)


devilry_url = 'http://localhost:8000'
login_url = '{0}/authenticate/login'.format(devilry_url)
logincookie = login(login_url, username='grandma', password='test')

# Create proxy classes which makes it natural to program against the
# RESTful interface using python.
restful_factory = RestfulFactory("http://localhost:8000/")
SimplifiedNode = restful_factory.make("administrator/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("administrator/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("administrator/restfulsimplifiedperiod/")
SimplifiedAssignment = restful_factory.make("administrator/restfulsimplifiedassignment/")
SimplifiedAssignmentGroup = restful_factory.make("administrator/restfulsimplifiedassignmentgroup/")


""" #### SEARCH #### """


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
    

""" #### CREATE #### """

all_search()

#Create a new Node
SimplifiedNode.create(logincookie, short_name='donald', long_name='Donald Duck University', parentnode=None)




#Create a new node with no parent
# SimplifiedNode.create(logincookie, short_name='matnat', long_name='Matematisk Naturvitenskapelig Fakultet', parentnode=None)

#Find MatNats id
# allnodes = SimplifiedNode.search(logincookie)['items']
# matnat = [node for node in allnodes if node['short_name'] == 'matnat']
# id = matnat[0]['id']

#Create a new Node(IFI) under MatNat
# SimplifiedNode.create(logincookie, short_name='ifi', long_name='Institutt for informatikk', parentnode=id)

#Delete MatNat IFI will aslo be trashed
# SimplifiedNode.delete(logincookie, id)

#Create a new Node
