#!/usr/bin/env python

import logging
from os.path import join, exists
from os import environ, mkdir
from devilry.restful_client.login import login
from devilry.restful_client.restfulfactory import RestfulFactory

logging.debug('hello from sync.py')

logincookie = login('http://localhost:8000/authenticate/login',
        username='grandma', password='test')

restful_factory = RestfulFactory("http://localhost:8000/")
SimplifiedNode = restful_factory.make("administrator/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("administrator/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("administrator/restfulsimplifiedperiod/")

subjects = SimplifiedSubject.search(logincookie, query='')

#path to dir where delivery data is to be stored
devilry_path = join(environ['HOME'], 'devilry', 'devdata')

periods = ['fall01', 'spring01']

#traverse subjects and create folders for each subject and period if they don't already exist
for s in subjects:
    subj_path = join(devilry_path, s['short_name'])
    if not exists(subj_path):
        logging.debug('INFO: Creating {}'.format(subj_path))
        mkdir(subj_path)
    for p in periods:
        period_path = join(subj_path, p)
        if not exists(period_path):
            logging.debug('INFO: Creating {}'.format(period_path))
            print 'Print from sync.py'
            mkdir(period_path)


