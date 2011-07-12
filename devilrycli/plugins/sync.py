#!/usr/bin/env python

import logging, sys
from os.path import join, exists
from os import environ, mkdir
from login import login
from devilrycli.restfulclient import RestfulFactory
from utils import logging_startup

#Arguments for logging
args = sys.argv[1:]
logging_startup(args)
logging.debug('hello from sync.py')

logincookie = login('http://localhost:8000/authenticate/login',
        username='grandma', password='test')

restful_factory = RestfulFactory("http://localhost:8000/")
SimplifiedNode = restful_factory.make("administrator/restfulsimplifiednode/")
SimplifiedSubject = restful_factory.make("administrator/restfulsimplifiedsubject/")
SimplifiedPeriod = restful_factory.make("administrator/restfulsimplifiedperiod/")

subjects = SimplifiedSubject.search(logincookie, query='')['items']

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
            mkdir(period_path)


