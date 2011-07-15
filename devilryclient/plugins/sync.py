#!/usr/bin/env python

import logging, sys
from os.path import join, exists, dirname
from os import environ, mkdir
from devilryclient.restfulclient import login
from devilryclient.restfulclient import RestfulFactory
from devilryclient.utils import logging_startup, findconffolder, create_folder, Session

#Arguments for logging
args = sys.argv[1:]
otherargs = logging_startup(args) #otherargs has commandspecific args
logging.debug('hello from sync.py')

#TODO put this in login.py
# logincookie = login('http://localhost:8000/authenticate/login',
#         username='grandma', password='test')

session = Session()
logincookie = session.get_session_cookie()

#TODO put this in a utility function
restful_factory = RestfulFactory("http://localhost:8000/")
#SimplifiedNode = restful_factory.make("examiner/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("examiner/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("examiner/restfulsimplifiedperiod/")
SimplifiedAssignment = restful_factory.make("examiner/restfulsimplifiedassignment/")
SimplifiedAssignmentGroup = restful_factory.make("examiner/restfulsimplifiedassignmentgroup/")
SimplifiedDelivery = restful_factory.make("examiner/restfulsimplifieddelivery/")
SimplifiedDeadline = restful_factory.make("examiner/restfulsimplifieddeadline/")
SimplifiedStaticFeedback = restful_factory.make("examiner/restfulsimplifiedstaticfeedback/")

#find all nodes where the user is examiner 
#nodes = SimplifiedNode.search(logincookie, query='')['items']


<<<<<<< HEAD

devilry_path = findconffolder()
=======
devilry_path = dirname(findconffolder())
>>>>>>> refs/remotes/devilry/master

#traverse nodes and create folders for each subject, period... if they don't already exist
#Problem: subject has no resultfield parentnode_short_name
#for n in nodes:
#    node_filters = [{'field':"parentnode__short_name", "comp":"iexact", "value":n["short_name"]}]
subjects = SimplifiedSubject.search(logincookie, query='')['items']

for s in subjects:
    subject_path = create_folder(s, devilry_path, 'short_name')

    sub_filters = [{'field':"parentnode__short_name", "comp":"iexact", "value":s["short_name"]}]
            #, {'field':"parentnode__parentnode__short_name", "comp":"iexact", "value":n["short_name"]}]
    periods = SimplifiedPeriod.search(logincookie, result_fieldgroups=['subject'], filters=sub_filters)['items']
    
    for p in periods:
        period_path = create_folder(p, subject_path, 'short_name')

        ass_filters = [{'field':"parentnode__short_name", "comp":"iexact", "value":p['short_name']},
                {'field':"parentnode__parentnode__short_name", "comp":"iexact", "value":s["short_name"]}]
                #, {'field':"parentnode__parentnode__parentnode__short_name", "comp":"iexact", "value":n["short_name"]}]
        assignments = SimplifiedAssignment.search(logincookie,result_fieldgroups=['subject', 'period'], filters=ass_filters)['items']

        for a in assignments:
            assignment_path = create_folder(a, period_path, 'short_name')

            ag_filters = [{'field':"parentnode__short_name", "comp":"icontains", "value":a["short_name"]},
                    {'field':"parentnode__parentnode__short_name", "comp":"iexact", "value":p['short_name']},
                {'field':"parentnode__parentnode__parentnode__short_name", "comp":"iexact", "value":s["short_name"]}]
            assignmentgroups = SimplifiedAssignmentGroup.search(logincookie, result_fieldgroups=['subject', 'period', 'assignment'], filters=ag_filters)['items']
            #assignmentgroups = SimplifiedAssignmentGroup.search(logincookie)['items']
            for ag in assignmentgroups:
                ag_path = create_folder(ag, assignment_path, 'id')
              
                #TODO add filers
                deliveries = SimplifiedDelivery.search(logincookie)['items']

                for d in deliveries:
                    print d['time_of_delivery']
                    delivery_path = create_folder(d, ag_path, 'number')
                    
                    #TODO add filters
                    deadlines = SimplifiedDeadline.search(logincookie)['items']
                    for dead in deadlines:
                        pass

                feedbacks = SimplifiedStaticFeedback.search(logincookie)['items']
                for f in feedbacks:
                    pass
                #can't go further because delivery does not support filters

                

#ok                delivery_filters = [{'field':"parentnode__id", "comp":"icontains", "value":ag["id"]},
#                        {'field':"parentnode__parentnode__short_name", "comp":"icontains", "value":a["short_name"]},
#                    {'field':"parentnode__parentnode__parentnode__short_name", "comp":"iexact", "value":p['short_name']},
#                {'field':"parentnode__parentnode__parentnode__parentnode__short_name", "comp":"iexact", "value":s["short_name"]}]

                #filters = [{'field':"assignment_group__id", comp:"iexact", "value":ag["id"]}]
                #print filters
                #deliveries = SimplifiedDelivery.search(logincookie, filters=filters)['items']
                #deliveries = SimplifiedDelivery.search(logincookie, query="")
                #print deliveries
                
