from login import login
from restfulfactory import RestfulFactory
from errors import HttpResponseForbidden, HttpResponseBadRequest, HttpResponseUnauthorized, HttpResponseNotFound

#TODO include subjects and periods in the example. The existing code for subjects does not work because
#parentnode__id has to be provided when creating a new subject. In the situation of dumping new data which
#we are trying to illustrate here, the parentnode__id may not be available

#data
nodes = [('uio', {"long_name": "Universitet i Oslo"}),
         ('uio.matnat', {"long_name": "Matematisk-Naturvitenskapelig fakultet"}),
         ('uio.matnat.ifi', {"long_name": "Institutt for informatikk"})]

subjects = [{"long_name": "INF1000 - Introduction to object-oriented programming",  "short_name": "inf1000"},
            {"long_name": "INF1010 - Object-oriented programming", "short_name": "inf1010"}]

periods = [{"short_name": "h2011", "long_name": "host 2011", "start_time": "2011-07-17", "end_time":"2011-12-15"},
           {"short_name": "v2011", "long_name": "vaar 2011", "start_time": "2011-01-17", "end_time":"2011-06-15"}]


logincookie = login('http://localhost:8000/authenticate/login',
                    username='grandma', password='test')

restful_factory = RestfulFactory("http://localhost:8000/")
SimplifiedNode = restful_factory.make("administrator/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("administrator/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("administrator/restfulsimplifiedperiod/")

#print 'All nodes:'
#for x in SimplifiedNode.search(logincookie, limit=4, query=''):
    #print '  ', x
#print

def nodepath_to_fields(nodepath):
    pathsplit = nodepath.split('.')
    prefix = ''
    fields = {}
    for short_name in reversed(pathsplit):
        fields[prefix + 'short_name'] = short_name
        prefix += 'parentnode__'
    return fields


#nodesearch = SimplifiedPeriod.search(logincookie, parentnode=4)
#print nodesearch
print "Create nodes, or update if they already exist:"
for path, nodedata in nodes:
    pathfields = nodepath_to_fields(path)
    matches = SimplifiedNode.search(logincookie, **pathfields)
    if len(matches) == 0:
        nodedata['short_name'] = pathfields['short_name']
        del pathfields['short_name']
        parentnode_path = path.rsplit('.', 1)
        if len(parentnode_path) == 1:
            parentnode_id = None
        else:
            parentnode_path = parentnode_path[0]
            parentnodesearch = SimplifiedNode.search(logincookie, **nodepath_to_fields(parentnode_path))
            if len(parentnodesearch) == 0:
                raise ValueError('Paretnode for "{0}" does not exist.'.format(path))
            parentnode_id = parentnodesearch[0]['id']
        newnode = SimplifiedNode.create(logincookie, parentnode=parentnode_id, **nodedata)
        print 'Created:', newnode
    elif len(matches) == 1:
        currentnode = matches[0]
        currentnode.update(**nodedata) # Add our data to the node
        updated_node = SimplifiedNode.update(logincookie, **currentnode)
        print 'Updated:', updated_node
    else:
        raise ValueError('More than one match. This is a bug, since our search should match only one item.')


#print
#print 'Read SimplifiedNode ifi:'
#node = SimplifiedNode.search(logincookie, query="ifi")
#if len(node) != 0:
    #node = node[0]
    #print '  ', SimplifiedNode.read(node["id"], logincookie)#, long_name="Institutt for informatikk")
#else:
    #print "No node ifi found"
#print

##delete
#print
#print 'Delete SimplifiedNode matnat, then try to read it:'
#node = SimplifiedNode.search(logincookie, query="matnat")
#if len(node) != 0:
    #node = node[0]
    #SimplifiedNode.delete(node["id"], logincookie)#, long_name="Institutt for informatikk")
    #print "Deleted SimplifiedNode matnat"
    #try:
        #print '  ', SimplifiedNode.read(node["id"], logincookie)
    #except HttpResponseForbidden:
        #print "SimplifiedNode matnat could not be read (because it was just deleted)"
#else:
    #print "No node matnat found"
#print

"""
#Do the same for subjects
print 'All subjects:'
for x in SimplifiedSubject.search(logincookie, limit=4, query=''):
    print '  ', x
print

subj = SimplifiedSubject.create(logincookie, short_name="test", long_name="test_subject")

print "Create subjects, or update if they already exist:"
print
for s in subjects:
    try:
        newsubject = SimplifiedSubject.create(logincookie, **s)
        print 'Created: ', newsubject
        print
    except HttpResponseBadRequest:
        subject = SimplifiedSubject.search(logincookie, query=s["short_name"])[0]
        print 'Updated: ', SimplifiedSubject.update(subject["id"], logincookie, short_name='updated', long_name='updated')
        print
        #WTF?? Have to update both shortname and longname for this to work

print
print 'Read SimplifiedSubject inf1010:'
subject = SimplifiedSubject.search(logincookie, query="ind1010")
if len(subject) != 0:
    subject = subject[0]
    print '  ', SimplifiedSubject.read(subject["id"], logincookie)#, long_name="Institutt for informatikk")
else:
    print "No subject inf1010 found"
print

#delete
print
print 'Delete SimplifiedSubject inf1000, then try to read it:'
subject = SimplifiedNode.search(logincookie, query="inf1000")
if len(subject) != 0:
    subject = subject[0]
    SimplifiedSubject.delete(subject["id"], logincookie)#, long_name="Institutt for informatikk")
    try:
        print '  ', SimplifiedSubject.read(subject["id"], logincookie)
    except HttpResponseForbidden:
        print "SimplifiedSubject inf1000 could not be read (because it was just deleted)"
else:
    print "No subject inf1000 found"
print

"""



#print
#print 'Create a new SimplifiedNode:'
#newnode = SimplifiedNode.create(logincookie, short_name='newly_created', long_name='Newly created')
#print '  ', newnode

#print
#print 'Update SimplifiedNode with id={0}:'.format(newnode['id'])
#print '  ', SimplifiedNode.update(logincookie, 1, long_name='This has been updated', short_name='has_been_updated')


#print
#print 'Delete and re-read SimplifiedNode with id={0}:'.format(newnode['id'])
#SimplifiedNode.delete(logincookie, newnode['id'])
#try:
#    SimplifiedNode.read(logincookie, 1)
#except HttpResponseForbidden, e:
#    print 'SimplifiedNode with id=1 could not be read (which should be correct since we just deleted it)'
