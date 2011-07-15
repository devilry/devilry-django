#!/usr/bin/env python

import logging, sys
from os.path import join, exists, dirname
from os import environ, mkdir
from devilryclient.restfulclient import login
from devilryclient.restfulclient import RestfulFactory
from devilryclient.utils import logging_startup, findconffolder, create_folder

#Arguments for logging
args = sys.argv[1:]
otherargs = logging_startup(args) #otherargs has commandspecific args
logging.debug('hello from sync.py')

#TODO put this in login.py
logincookie = login('http://localhost:8000/authenticate/login',
        username='examiner1', password='test')


#TODO put this in a utility function
restful_factory = RestfulFactory("http://localhost:8000/")
#SimplifiedNode = restful_factory.make("examiner/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("examiner/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("examiner/restfulsimplifiedperiod/")
SimplifiedAssignment = restful_factory.make("examiner/restfulsimplifiedassignment/")

#assignmentgroup does not work! when using SimplifiedAssignmentGroup to search later it fails
#think this has something to do with the url.
SimplifiedAssignmentGroup = restful_factory.make("examiner/restfulsimplifiedassignmentgroup/")
SimplifiedDelivery = restful_factory.make("examiner/restfulsimplifieddelivery/")


#find all nodes where the user is examiner 
#nodes = SimplifiedNode.search(logincookie, query='')['items']

print SimplifiedAssignmentGroup

devilry_path = dirname(findconffolder())

#traverse nodes and create folders for each subject, period... if they don't already exist
#Problem: subject has no resultfield parentnode_short_name
#for n in nodes:
#    node_filters = [{'field':"parentnode__short_name", "comp":"iexact", "value":n["short_name"]}]
subjects = SimplifiedSubject.search(logincookie, query='')['items']
print subjects

for s in subjects:
    subject_path = create_folder(s, devilry_path, 'short_name')

    sub_filters = [{'field':"parentnode__short_name", "comp":"iexact", "value":s["short_name"]}]
            #, {'field':"parentnode__parentnode__short_name", "comp":"iexact", "value":n["short_name"]}]
    periods = SimplifiedPeriod.search(logincookie, result_fieldgroups=['subject'], filters=sub_filters)['items']
    print
    print periods
    
    for p in periods:
        period_path = create_folder(p, subject_path, 'short_name')

        ass_filters = [{'field':"parentnode__short_name", "comp":"iexact", "value":p['short_name']},
                {'field':"parentnode__parentnode__short_name", "comp":"iexact", "value":s["short_name"]}]
                #, {'field':"parentnode__parentnode__parentnode__short_name", "comp":"iexact", "value":n["short_name"]}]
        assignments = SimplifiedAssignment.search(logincookie,result_fieldgroups=['subject', 'period'], filters=ass_filters)['items']
        print
        print assignments

        for a in assignments:
            assignment_path = create_folder(a, period_path, 'short_name')

            ag_filters = [{'field':"parentnode__short_name", "comp":"icontains", "value":a["short_name"]},
                    {'field':"parentnode__parentnode__short_name", "comp":"iexact", "value":p['short_name']},
                {'field':"parentnode__parentnode__parentnode__short_name", "comp":"iexact", "value":s["short_name"]}]
            #assignmentgroups = SimplifiedAssignmentGroup.search(logincookie, result_fieldgroups=['subject', 'period', 'assignment'], filters=ag_filters)['items']
            assignmentgroups = SimplifiedAssignmentGroup.search(logincookie)

            print
            print assignmentgroups

            for ag in assignmentgroups:
                ag_path = create_folder(ag, assignment_path, 'id')
                
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
                
