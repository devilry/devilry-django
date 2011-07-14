#!/usr/bin/env python

import logging, sys
from os.path import join, exists
from os import environ, mkdir
from devilryclient.restfulclient import login
from devilryclient.restfulclient import RestfulFactory
from devilryclient.utils import logging_startup, findconffolder

#Arguments for logging
args = sys.argv[1:]
otherargs = logging_startup(args) #otherargs has commandspecific args
logging.debug('hello from sync.py')

#TODO put this in login.py
logincookie = login('http://localhost:8000/authenticate/login',
        username='grandma', password='test')


#TODO put this in a utility function
restful_factory = RestfulFactory("http://localhost:8000/")
SimplifiedNode = restful_factory.make("administrator/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("administrator/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("administrator/restfulsimplifiedperiod/")
SimplifiedAssignment = restful_factory.make("administrator/restfulsimplifiedassignment/")

subjects = SimplifiedSubject.search(logincookie, query='duck')['items']

#cfgfile = open(

devilry_path = findconffolder()

#path to dir where delivery data is to be stored
#devilry_path = join(environ['HOME'], 'devilry', 'devdata')
#devilry_path = 

#periods = ['fall01', 'spring01']

#traverse subjects and create folders for each subject and period if they don't already exist
for s in subjects:
    #TODO put this in a utility function to avoid repetition
    subj_path = join(devilry_path, s['short_name'])
    if not exists(subj_path):
        logging.debug('INFO: Creating {}'.format(subj_path))
        mkdir(subj_path)

    filters = [{'field':"parentnode__short_name", "comp":"icontains", "value":s["short_name"]}]
    periods = SimplifiedPeriod.search(logincookie, filters=filters)['items']
    
    for p in periods:
        period_path = join(subj_path, p['short_name'])
        if not exists(period_path):
            logging.debug('INFO: Creating {}'.format(period_path))
            mkdir(period_path)


        filters = [{'field':"parentnode__short_name", "comp":"icontains", "value":p["short_name"]}]
        assignments = SimplifiedAssignment.search(logincookie, filters=filters)['items']

        for a in assignments:
            assignment_path = join(period_path, a['short_name'])
            if not exists(assignment_path):
                logging.debug('INFO: Creating {}'.format(assignment_path))
                mkdir(assignment_path)


