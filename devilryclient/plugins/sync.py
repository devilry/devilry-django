#!/usr/bin/env python

import logging
import sys
import ConfigParser
from os.path import join, dirname, sep
from devilryclient.restfulclient.restfulfactory import RestfulFactory
from devilryclient.utils import logging_startup, findconffolder, create_folder

class PullFromServer(object):
    """
    Collect all data that the logged-in user has access to...
    """

    def __init__(self):
        #Arguments for logging
        args = sys.argv[1:]
        otherargs = logging_startup(args)  # otherargs has commandspecific args
        logging.debug('hello from sync.py')

        confdir = findconffolder()
        conf = ConfigParser.ConfigParser()
        conf.read(join(confdir, 'config'))

        url = conf.get('resources', 'url')

        restful_factory = RestfulFactory(url)

        self.SimplifiedSubject = restful_factory.make("/examiner/restfulsimplifiedsubject/")
        self.SimplifiedPeriod = restful_factory.make("/examiner/restfulsimplifiedperiod/")
        self.SimplifiedAssignment = restful_factory.make("/examiner/restfulsimplifiedassignment/")
        self.SimplifiedAssignmentGroup = restful_factory.make("/examiner/restfulsimplifiedassignmentgroup/")
        self.SimplifiedDelivery = restful_factory.make("/examiner/restfulsimplifieddelivery/")
        self.SimplifiedDeadline = restful_factory.make("/examiner/restfulsimplifieddeadline/")
        self.SimplifiedStaticFeedback = restful_factory.make("/examiner/restfulsimplifiedstaticfeedback/")

        self.tree = {}
        self.num_groups = 0
        self.num_subjects = 0
        self.num_deliveries = 0
        self.num_feedbacks = 0

    def add_start(self):
        #start creating directories recursively
        devilry_path = dirname(findconffolder())
        subjects = self.SimplifiedSubject.search(query='')['items']
        self.add_subjects(devilry_path, subjects)

    def add_subjects(self, devilry_path, subjects):
        for subject in subjects:
            self.num_subjects += 1
            #add subject to tree dictionary
            self.tree[subject['short_name']] = {}

            subject_path = create_folder(subject, devilry_path, 'short_name')
            #search for this subjects periods
            period_filters = [{'field':'parentnode',
                                'comp':'exact',
                                'value':subject['id']}]
            periods = self.SimplifiedPeriod.search(result_fieldgroups=['subject'], filters=period_filters)['items']
            self.add_periods(subject_path, periods)

    def add_periods(self, subject_path, periods):
        for period in periods:
            path = subject_path.split(sep)
            #get names
            subject = path[-1]
            #add period to tree dictionary
            self.tree[subject][period['short_name']] = {}

            period_path = create_folder(period, subject_path, 'short_name')
            assignment_filters = [{'field':'parentnode',
                                   'comp':'exact',
                                   'value':period['id']}]
            assignments = self.SimplifiedAssignment.search(
                        result_fieldgroups=['subject', 'period'], 
                        filters=assignment_filters)['items']
            self.add_assignments(period_path, assignments)

    def add_assignments(self, period_path, assignments):
        for assignment in assignments:
            path = period_path.split(sep)
            period = path[-1]
            subject = path[-2]
            self.tree[subject][period][assignment['short_name']] = {}
            assignment_path = create_folder(assignment, period_path, 'short_name')

            a_group_filters = [{'field':'parentnode',
                                'comp':'exact',
                                'value':assignment['id']}]

            assignment_groups = self.SimplifiedAssignmentGroup.search( 
                            result_fieldgroups=['period', 'assignment'], 
                            filters=a_group_filters)['items']
            self.add_assignmentgroups(assignment_path, assignment_groups)

    def add_assignmentgroups(self, assignment_path, assignment_groups):
        for assignment_group in assignment_groups:
            path = assignment_path.split(sep)
            assignment = path[-1]
            period = path[-2]
            subject = path[-3]
            self.tree[subject][period][assignment][str(assignment_group['id'])] = {}

            assignment_group_path = create_folder(assignment_group, assignment_path, 'id')
            deadline_filters = [{'field':'assignment_group',
                                 'comp':'exact',
                                 'value':assignment_group['id']}]
            deadlines = self.SimplifiedDeadline.search( 
                        result_fieldgroups=['period', 'assignment', 'assignment_group'],
                        filters=deadline_filters)['items']
            self.add_deadlines(assignment_group_path, deadlines)

    def add_deadlines(self, assignment_group_path, deadlines):
        for deadline in deadlines:
            path = assignment_group_path.split(sep)
            group = path[-1]
            assignment = path[-2]
            period = path[-3]
            subject = path[-4]
            self.tree[subject][period][assignment][group][deadline['deadline']] = {}

            deadline_path = create_folder(deadline, assignment_group_path, 'deadline')
            delivery_filters = [{'field':'deadline',
                                 'comp':'exact',
                                 'value':deadline['id']}]
            deliveries = self.SimplifiedDelivery.search( 
                       result_fieldgroups=['period', 'assignment', 'assignment_group'],
                        filters=delivery_filters)['items']
            self.add_deliveries(deadline_path, deliveries)

    def add_deliveries(self, deadline_path, deliveries):
        for delivery in deliveries:
            late = self.is_late(delivery)
            path = deadline_path.split(sep)
            deadline = path[-1]
            group = path[-2]
            assignment = path[-3]
            period = path[-4]
            subject = path[-5]
            self.tree[subject][period][assignment][group][deadline][str(delivery['id'])] = {}

            delivery_path = create_folder(delivery, deadline_path, 'id')

            devilryfolder = findconffolder()
            treefile = open(join(devilryfolder, 'metadata'), 'w')
            treefile.write(str(self.tree))
            treefile.close()
            #filemeta
            #make feedback.txt file

    def is_late(self, delivery):
        #print delivery
        return False

if __name__ == '__main__':
    PullFromServer().add_start()
