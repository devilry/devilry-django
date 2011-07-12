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


def load_matnat_ifi_nodes():
    #Create a new node with no parent
    SimplifiedNode.create(logincookie, short_name='matnat', long_name='Matematisk Naturvitenskapelig Fakultet', parentnode=None)

    #Find MatNats id
    allnodes = SimplifiedNode.search(logincookie)['items']
    matnat = [node for node in allnodes if node['short_name'] == 'matnat']
    id = matnat[0]['id']

    #Create a new Node(IFI) under MatNat
    SimplifiedNode.create(logincookie, short_name='ifi', long_name='Institutt for informatikk', parentnode=id)


if __name__ == '__main__':
    load_matnat_ifi_nodes()
    #Delete MatNat IFI will as lo be trashed
    SimplifiedNode.delete(logincookie, id)


