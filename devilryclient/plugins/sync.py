#!/usr/bin/env python

import logging
import sys
import ConfigParser
from os.path import join, dirname, sep, exists
from os import rename
from devilryrestfullib.restfulfactory import RestfulFactory
from devilryclient.utils import logging_startup, findconffolder, create_folder, deadline_format, is_late, get_metadata, save_metadata


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

        self.root_dir = dirname(confdir) + sep
        self.metadata = {}

    def run(self):
        #start creating directories recursively
        devilry_path = dirname(findconffolder())
        subjects = self.SimplifiedSubject.search(query='')
        self.add_subjects(devilry_path, subjects)
        self.write_metadata()

    def add_subjects(self, devilry_path, subjects):
        for subject in subjects['items']:
            subject_path = create_folder(join(devilry_path, subject['short_name']))
            #search for this subjects periods
            period_filters = [{'field':'parentnode',
                               'comp':'exact',
                               'value':subject['id']}]
            periods = self.SimplifiedPeriod.search(result_fieldgroups=['subject'], filters=period_filters)

            key = subject_path.replace(self.root_dir, '')
            self.metadata[key] = {}
            self.metadata[key]['query_result'] = subject
            self.add_periods(subject_path, periods)

    def add_periods(self, subject_path, periods):
        for period in periods['items']:
            period_path = create_folder(join(subject_path, period['short_name']))
            assignment_filters = [{'field':'parentnode',
                                   'comp':'exact',
                                   'value':period['id']}]
            assignments = self.SimplifiedAssignment.search(
                result_fieldgroups=['subject', 'period'],
                filters=assignment_filters)
            #add period to tree dictionary
            key = period_path.replace(self.root_dir, '')

            self.metadata[key] = {}
            self.metadata[key]['query_result'] = period

            self.add_assignments(period_path, assignments)

    def add_assignments(self, period_path, assignments):
        for assignment in assignments['items']:
            assignment_path = create_folder(join(period_path, assignment['short_name']))
            a_group_filters = [{'field':'parentnode',
                                'comp':'exact',
                                'value':assignment['id']}]

            assignment_groups = self.SimplifiedAssignmentGroup.search(
                result_fieldgroups=['period', 'assignment', 'users'],
                filters=a_group_filters)

            key = assignment_path.replace(self.root_dir, '')

            self.metadata[key] = {}
            self.metadata[key]['query_result'] = assignment

            self.add_assignmentgroups(assignment_path, assignment_groups)

    def add_assignmentgroups(self, assignment_path, assignment_groups):
        for assignment_group in assignment_groups['items']:

            assignment_group_path = create_folder(join(assignment_path, str(assignment_group['id'])))
            deadline_filters = [{'field':'assignment_group',
                                 'comp':'exact',
                                 'value':assignment_group['id']}]
            deadlines = self.SimplifiedDeadline.search(
                result_fieldgroups=['period', 'assignment', 'assignment_group'],
                filters=deadline_filters, order_by='deadline')
            key = assignment_group_path.replace(self.root_dir, '')

            self.metadata[key] = {}
            self.metadata[key]['query_result'] = assignment_group

            self.add_deadlines(assignment_group_path, deadlines)

    def add_deadlines(self, assignment_group_path, deadlines):
        number = 1  # number for tagging the deadlines
        for deadline in deadlines['items']:
            #format deadline
            deadlinetime = deadline_format(deadline['deadline'])
            deadlinetime = '{}_{}'.format(number, deadlinetime)
            number += 1

            deadline_path = create_folder(join(assignment_group_path, deadlinetime))
            delivery_filters = [{'field':'deadline',
                                 'comp':'exact',
                                 'value':deadline['id']}]
            deliveries = self.SimplifiedDelivery.search(
                result_fieldgroups=['period', 'assignment', 'assignment_group', 'deadline', 'delivered_by', 'candidates'],
                filters=delivery_filters)

            key = deadline_path.replace(self.root_dir, '')

            self.metadata[key] = {}
            self.metadata[key]['query_result'] = deadline

            self.add_deliveries(deadline_path, deliveries)

    def add_deliveries(self, deadline_path, deliveries):
        for delivery in deliveries['items']:
            #tag late deliveries
            if is_late(delivery):
                name = '{}_late'.format(str(delivery['number']))
            else:
                name = str(delivery['number'])
            delivery_path = create_folder(join(deadline_path, name))
            file_filters = [{'field':'delivery',
                             'comp':'exact',
                             'value':delivery['id']}]
            files = self.SimplifiedFileMeta.search(
                result_fieldgroups=['period', 'assignment', 'assignment_group'],
                filters=file_filters)

            feedbacks = self.SimplifiedStaticFeedback.search(
                result_fieldgroups=['period', 'assignment', 'assignment_group'],
                filters=file_filters)

            key = delivery_path.replace(self.root_dir, '')
            
            self.metadata[key] = {}
            self.metadata[key]['query_result'] = delivery

            self.add_files(delivery_path, files)
            #self.add_feedbacks(delivery_path, feedbacks)

    def add_files(self, delivery_path, files):
        file_path = create_folder(join(delivery_path, 'files'))
        for delivery_file in files['items']:
            path = join(file_path, delivery_file['filename'])
            f = open(path, 'w')
            f.close()
            key = path.replace(self.root_dir, '')
            self.metadata[key] = {}
            self.metadata[key]['query_result'] = delivery_file

    """
    def add_feedbacks(self, delivery_path, feedbacks):
        #TODO
        file_path = create_folder(join(delivery_path, 'files'))
        for feedback in feedbacks['items']:
            self.metadata[key] = {}
            self.metadata[key]['.meta'] = {}
            self.metadata[key]['.meta']['feedback_query_result'] = feedback
    """
    def write_metadata(self):
        devilryfolder = findconffolder()
        metafilename = join(devilryfolder, 'metadata')
        if exists(metafilename):
            rename(metafilename, join(devilryfolder, 'old_metadata'))
        save_metadata(self.metadata)

if __name__ == '__main__':
    PullFromServer().run()
