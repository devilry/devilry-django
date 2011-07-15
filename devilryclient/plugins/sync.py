#!/usr/bin/env python

import logging, sys
from os.path import join, exists
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
SimplifiedNode = restful_factory.make("administrator/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("administrator/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("administrator/restfulsimplifiedperiod/")
SimplifiedAssignment = restful_factory.make("administrator/restfulsimplifiedassignment/")
SimplifiedAssignmentGroup = restful_factory.make("administrator/restfulsimplifiedassignmentgroup/")
SimplifiedDelivery = restful_factory.make("administrator/restfulsimplifieddelivery/")


#find all nodes where the user is examiner 
nodes = SimplifiedNode.search(logincookie, query='')['items']


devilry_path = findconffolder()

#traverse nodes and create folders for each subject, period... if they don't already exist
#Problem: subject has no resultfield parentnode_short_name
for n in nodes:
    node_filters = [{'field':"parentnode__short_name", "comp":"iexact", "value":n["short_name"]}]
    subjects = SimplifiedSubject.search(logincookie, filters=node_filters)['items']

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

                for ag in assignmentgroups:
                    ag_path = create_folder(ag, assignment_path, 'id')
                    
                    #can't go further because delivery does not support filters

                    """

                    delivery_filters = [{'field':"parentnode__id", "comp":"icontains", "value":ag["id"]},
                            {'field':"parentnode__parentnode__short_name", "comp":"icontains", "value":a["short_name"]},
                        {'field':"parentnode__parentnode__parentnode__short_name", "comp":"iexact", "value":p['short_name']},
                    {'field':"parentnode__parentnode__parentnode__parentnode__short_name", "comp":"iexact", "value":s["short_name"]}]


                    #filters = [{'field':"assignment_group__id", comp:"iexact", "value":ag["id"]}]
                    #print filters
                    #deliveries = SimplifiedDelivery.search(logincookie, filters=filters)['items']
                    #deliveries = SimplifiedDelivery.search(logincookie, query="")
                    #print deliveries
                    """
