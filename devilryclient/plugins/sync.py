#!/usr/bin/env python

import logging, sys, ConfigParser
from os.path import join, exists, dirname
from os import environ, mkdir
from devilryclient.restfulclient import login
from devilryclient.restfulclient import RestfulFactory
from devilryclient.utils import logging_startup, findconffolder, create_folder, Session

#Arguments for logging
args = sys.argv[1:]
otherargs = logging_startup(args) #otherargs has commandspecific args
logging.debug('hello from sync.py')

session = Session()
#TODO get_session_cookie not working, find out why
logincookie = session.get_session_cookie()

#TODO put this in login.py
# logincookie = login('http://localhost:8000/authenticate/login',
#         username='grandma', password='test')

logincookie = login('http://localhost:8000/authenticate/login',
         username='examiner2', password='test')

confdir = findconffolder()
conf = ConfigParser.ConfigParser()
conf.read(join(confdir, 'config'))

url = conf.get('URL', 'url')
print url

#TODO put this in a utility function
restful_factory = RestfulFactory(url)

SimplifiedSubject = restful_factory.make("/examiner/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("/examiner/restfulsimplifiedperiod/")
SimplifiedAssignment = restful_factory.make("/examiner/restfulsimplifiedassignment/")
SimplifiedAssignmentGroup = restful_factory.make("/examiner/restfulsimplifiedassignmentgroup/")
SimplifiedDelivery = restful_factory.make("/examiner/restfulsimplifieddelivery/")
SimplifiedDeadline = restful_factory.make("/examiner/restfulsimplifieddeadline/")
SimplifiedStaticFeedback = restful_factory.make("/examiner/restfulsimplifiedstaticfeedback/")

devilry_path = dirname(findconffolder())

subjects = SimplifiedSubject.search(logincookie, query='')['items']

for subject in subjects:
    subject_path = create_folder(subject, devilry_path, 'short_name')
    subject_filters = [{'field':"parentnode", "comp":"exact", "value":subject["id"]}]
    periods = SimplifiedPeriod.search(logincookie, result_fieldgroups=['subject'], filters=subject_filters)['items']
    
    for period in periods:
        period_path = create_folder(period, subject_path, 'short_name')
        assignment_filters = [{'field':"parentnode", "comp":"exact", "value":period["id"]}]
        assignments = SimplifiedAssignment.search(logincookie,
                    result_fieldgroups=['subject', 'period'], 
                    filters=assignment_filters)['items']

        for assignment in assignments:
            assignment_path = create_folder(assignment, period_path, 'short_name')

            a_group_filters = [{'field':"parentnode", "comp":"exact", "value":assignment["id"]}]

            assignmentgroups = SimplifiedAssignmentGroup.search(logincookie, 
                            result_fieldgroups=['period', 'assignment'], 
                            filters=a_group_filters)['items']
            
            for a_group in assignmentgroups:
                a_group_path = create_folder(a_group, assignment_path, 'id')
                deadline_filters = [{'field':'assignment_group', 'comp':'exact', 'value':a_group['id']}]
                deadlines = SimplifiedDeadline.search(logincookie, 
                            result_fieldgroups=['period', 'assignment', 'assignment_group'],
                            filters=deadline_filters)['items']
                for deadline in deadlines:
                    print deadline
                
                """
                #TODO delivery has no parentnode
                #delivery_filters = [{'field':"parentnode", "comp":"exact", "value":ag["id"]}]
                       
                deliveries = SimplifiedDelivery.search(logincookie, 
                            result_fieldgroups=['subject', 'period', 'assignment', 'asignment_group'],
                            filters=delivery_filters)['items']

                for d in deliveries:
                    print d
                    delivery_path = create_folder(d, ag_path, 'number')
                    
                    #TODO add filters
                    deadlines = SimplifiedDeadline.search(logincookie)['items']
                    for dead in deadlines:
                        pass

                feedbacks = SimplifiedStaticFeedback.search(logincookie)['items']
                for f in feedbacks:
                    pass
                #can't go further because delivery does not support filters
                """
