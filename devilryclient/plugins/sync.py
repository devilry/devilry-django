#!/usr/bin/env python

import logging
import sys
import ConfigParser
from os.path import join, dirname, sep
from devilryclient.restfulclient.restfulfactory import RestfulFactory
from devilryclient.utils import logging_startup, findconffolder, create_folder, deadline_format, is_late

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
        self.SimplifiedFileMeta = restful_factory.make("/examiner/restfulsimplifiedfilemeta/")

        self.tree = {}

    def add_start(self):
        #start creating directories recursively
        devilry_path = dirname(findconffolder())
        subjects = self.SimplifiedSubject.search(query='')
        self.add_subjects(devilry_path, subjects)

    def add_subjects(self, devilry_path, subjects):
        self.tree['.meta'] = {}
        self.tree['.meta']['query_result'] = subjects
        for subject in subjects['items']:
            subject_path = create_folder(join(devilry_path, subject['short_name']))
            #search for this subjects periods
            period_filters = [{'field':'parentnode',
                               'comp':'exact',
                               'value':subject['id']}]
            periods = self.SimplifiedPeriod.search(result_fieldgroups=['subject'], filters=period_filters)
            #self.tree['.meta'] = {}
            self.tree[subject['short_name']] = {}
            self.add_periods(subject_path, periods)

    def add_periods(self, subject_path, periods):
        path = subject_path.split(sep)
        #get names
        subject = path[-1]
        self.tree[subject]['.meta'] = {}
        self.tree[subject]['.meta']['query_result'] = periods
        for period in periods['items']:

            period_path = create_folder(join(subject_path, period['short_name']))
            assignment_filters = [{'field':'parentnode',
                                   'comp':'exact',
                                   'value':period['id']}]
            assignments = self.SimplifiedAssignment.search(
                result_fieldgroups=['subject', 'period'],
                filters=assignment_filters)
            #add period to tree dictionary
            self.tree[subject][period['short_name']] = {}
            self.add_assignments(period_path, assignments)

    def add_assignments(self, period_path, assignments):
        path = period_path.split(sep)
        period = path[-1]
        subject = path[-2]
        self.tree[subject][period]['.meta'] = {}
        self.tree[subject][period]['.meta']['query_result'] = assignments
        for assignment in assignments['items']:
            assignment_path = create_folder(join(period_path, assignment['short_name']))
            a_group_filters = [{'field':'parentnode',
                                'comp':'exact',
                                'value':assignment['id']}]

<<<<<<< HEAD
            assignment_groups = self.SimplifiedAssignmentGroup.search( 
                            result_fieldgroups=['period', 'assignment', 'users'], 
                            filters=a_group_filters)
            
=======
            assignment_groups = self.SimplifiedAssignmentGroup.search(
                result_fieldgroups=['period', 'assignment', 'users'],
                filters=a_group_filters)

>>>>>>> 267e001347b108b23bf074b19d3fde6798102bda
            self.tree[subject][period][assignment['short_name']] = {}
            self.add_assignmentgroups(assignment_path, assignment_groups)

    def add_assignmentgroups(self, assignment_path, assignment_groups):
        path = assignment_path.split(sep)
        assignment = path[-1]
        period = path[-2]
        subject = path[-3]

        self.tree[subject][period][assignment]['.meta'] = {}
        self.tree[subject][period][assignment]['.meta']['query_result'] = assignment_groups
        for assignment_group in assignment_groups['items']:

            assignment_group_path = create_folder(join(assignment_path, str(assignment_group['id'])))
            deadline_filters = [{'field':'assignment_group',
                                 'comp':'exact',
                                 'value':assignment_group['id']}]
            deadlines = self.SimplifiedDeadline.search(
                result_fieldgroups=['period', 'assignment', 'assignment_group'],
                filters=deadline_filters)

            self.tree[subject][period][assignment][str(assignment_group['id'])] = {}
            self.add_deadlines(assignment_group_path, deadlines)

    def add_deadlines(self, assignment_group_path, deadlines):
        path = assignment_group_path.split(sep)
        group = path[-1]
        assignment = path[-2]
        period = path[-3]
        subject = path[-4]

        self.tree[subject][period][assignment][group]['.meta'] = {}
        self.tree[subject][period][assignment][group]['.meta']['query_result'] = deadlines
        for deadline in deadlines['items']:
            #format deadline
            deadlinetime = deadline_format(deadline['deadline'])

            path = assignment_group_path.split(sep)
            group = path[-1]
            assignment = path[-2]
            period = path[-3]
            subject = path[-4]

            deadline_path = create_folder(join(assignment_group_path, deadlinetime))
            delivery_filters = [{'field':'deadline',
                                 'comp':'exact',
                                 'value':deadline['id']}]
            deliveries = self.SimplifiedDelivery.search(
                result_fieldgroups=['period', 'assignment', 'assignment_group'],
                filters=delivery_filters)

            self.tree[subject][period][assignment][group][deadlinetime] = {}

            self.add_deliveries(deadline_path, deliveries)

    def add_deliveries(self, deadline_path, deliveries):
        path = deadline_path.split(sep)
        deadline = path[-1]
        group = path[-2]
        assignment = path[-3]
        period = path[-4]
        subject = path[-5]

        self.tree[subject][period][assignment][group][deadline]['.meta'] = {}
        self.tree[subject][period][assignment][group][deadline]['.meta']['query_result'] = deliveries
        for delivery in deliveries['items']:
            late = is_late(delivery)
            #TODO fix late deliveries
            delivery_path = create_folder(join(deadline_path, str(delivery['number'])))
            file_filters = [{'field':'delivery',
                             'comp':'exact',
                             'value':delivery['id']}]
            files = self.SimplifiedFileMeta.search(
                result_fieldgroups=['period', 'assignment', 'assignment_group'],
                filters=file_filters)

            self.tree[subject][period][assignment][group][deadline][str(delivery['number'])] = {}

            self.add_files(delivery_path, files)

    def add_files(self, delivery_path, files):
        path = delivery_path.split(sep)
        delivery = path[-1]
        deadline = path[-2]
        group = path[-3]
        assignment = path[-4]
        period = path[-5]
        subject = path[-6]
        self.tree[subject][period][assignment][group][deadline][delivery]['.meta'] = {}
        self.tree[subject][period][assignment][group][deadline][delivery]['.meta']['query_result'] = files

        file_path = create_folder(join(delivery_path, 'files'))
        self.tree[subject][period][assignment][group][deadline][delivery]['files'] = []
        for delivery_file in files['items']:
            f = open(join(file_path, delivery_file['filename']), 'w')
            f.close()

            self.tree[subject][period][assignment][group][deadline][delivery]['files'].append(delivery_file['filename'])

        devilryfolder = findconffolder()
        treefile = open(join(devilryfolder, 'metadata'), 'w')
        treefile.write(str(self.tree))
        treefile.close()

if __name__ == '__main__':
    PullFromServer().add_start()
