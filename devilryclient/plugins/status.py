#!/usr/bin/env python

# Not yet begun correcting:
"""
#
# Devilry server: examiner1@http://example.com/devilry
#
# Deliveries to correct: 20
#             remaining: 20
#
# Late deliveries: 3
#   assignment1:
#       3(alex), 2h late
#       7(harry), 1h late
#      13(clara), 3h late
#
"""

# Mid-correcting:
"""
#
# Devilry server: examiner1@http://example.com/devilry
#
# Deliveries to correct: 20
#             remaining: 17
#
# Feedbacks:
#   3 unpushed feedbacks:
#     assignment1:
#         1(jhonny)
#         2(pedro)
#         3(alex)
#
# Late deliveries: 2
#   assignment1:
#       7(harry), 1h late
#      13(clara), 3h late
#
"""

# Done correcting
"""
#
# Devilry server: examiner1@http://example.com/devilry
#
# Deliveries to correct: 20
#             remaining:  0
#
"""

from devilryclient.utils import findconffolder, get_config, get_metadata
from os.path import dirname, join, sep, exists
from os import listdir
import sys


class DevilryClientStatus(object):
    """
    Display an examiners progress in correcting deliveries by his/her
    students.
    """

    def __init__(self, soi=None, aoi=None):
        """
        Get the interesting values from .devilry/config

        :param soi: Subject of interest; Get only information about
        this subject

        :param aoi: Assignment of interest; Get only information about
        this assignment
        """

        self.conf_dir = findconffolder()
        self.root_dir = dirname(self.conf_dir)
        self.conf = get_config()
        self.metadata = get_metadata()

        # Read stuff from .devilry/config
        self.user = self.conf.get('resources', 'user')
        self.server = self.conf.get('resources', 'url')

        self.soi = soi
        self.aoi = aoi

    def run(self):
        self.collect_data()
        self.display()

    def collect_data(self):
        for key in sorted(self.metadata.keys()):
            print key
            for metakey in self.metadata[key].keys():
                if metakey == 'query_result':
                    continue
                print "    ", metakey, ':', self.metadata[key][metakey]

    def display(self):
        pass
    #     print '#'
    #     print "# Devilry server: {user}@{server}".format(user=self.user, server=self.server,)
    #     print '#'
    #     print "# Deliveries to correct: {num_deliveries}".format(num_deliveries=self.num_deliveries)
    #     print "#             remaining: {num_remaining}".format(num_remaining=self.num_deliveries -
    #                                                             self.num_feedbacks)

    #     if self.num_deliveries > 0:
    #         print '#'
    #         print '# Not corrected:'

    #     for subject in sorted(self.tree.keys()):

    #         if self.tree[subject]['.num_deliveries'] == 0:
    #             continue  # skip subjects with no deliveries

    #         print "#  {subject}:".format(subject=subject)

    #         for assignment in sorted(self.tree[subject].keys()):
    #             # if assignment.startswith('.'):
    #             #     continue  # meta-variable

    #             print "#    {assignment}:".format(assignment=assignment)

    #             for group in sorted(self.tree[subject][assignment].keys()):
    #                 if len(self.tree[subject][assignment][group].keys()) > 0:
    #                     print "#      {group}".format(group=group)
    #     print '#'

    #     print self.tree

    # def collect_from_subjects(self, directory):
    #     for subject in listdir(directory):
    #         # skip the .devilry folder
    #         if subject.startswith('.'):
    #             continue

    #         # check if soi is set, and skip any that are'nt the soi
    #         if self.soi != None and self.soi != subject:
    #             continue

    #         # .num_deliveries will keep track of how many deliveres
    #         # has been done in this subject
    #         self.tree[subject] = {'.num_deliveries': 0}
    #         self.num_subjects += 1

    #         # Go deeper
    #         self.collect_from_periods(join(directory, subject))

    # def collect_from_periods(self, directory):
    #     for period in listdir(directory):
    #         # we're not really interested in periods, but we need to
    #         # traverse them
    #         self.collect_from_assignments(join(directory, period))

    # def collect_from_assignments(self, directory):
    #     # find out which subject we're currently in period is the last
    #     # element, subject the second last
    #     path = directory.split(sep)
    #     subject = path[-2]
    #     for assignment in listdir(directory):
    #         # check if aoi is set, and skip any that are'nt the aoi
    #         if self.aoi != None and self.aoi != assignment:
    #             continue

    #         # .num_deliveries will keep track of how many deliveries
    #         # have been done in this assignment
    #         self.tree[subject][assignment] = {}
    #         # Go even deeper
    #         self.collect_from_assignmentgroups(join(directory, assignment))

    # def collect_from_assignmentgroups(self, directory):
    #     path = directory.split(sep)
    #     subject = path[-3]
    #     assignment = path[-1]
    #     for group in listdir(directory):
    #         self.tree[subject][assignment][group] = {}
    #         # Not deep enough!
    #         ## should we have deadlines directories?
    #         self.collect_from_deadlines(join(directory, group))
    #         # or just skip straight to deliveries?
    #         # self.collect_from_deliveries(join(directory, group))

    # def collect_from_deadlines(self, directory):
    #     for delivery in listdir(directory):
    #         # We dont care about deadlines
    #         self.collect_from_deliveries(join(directory, delivery))

    # def collect_from_deliveries(self, directory):
    #     path = directory.split(sep)
    #     subject = path[-4]
    #     assignment = path[-2]
    #     group = path[-1]
    #     for delivery in listdir(directory):
    #         self.tree[subject][assignment][group] = {}
    #         self.tree[subject]['.num_deliveries'] += 1
    #         # Deeper! We must go deeper!
    #         self.collect_from_feedbacks(join(directory, delivery))

    # def collect_from_feedbacks(self, directory):
    #     path = directory.split(sep)
    #     subject = path[-5]
    #     assignment = path[-3]
    #     group = path[-2]
    #     delivery = path[-1]
    #     if exists(join(directory, 'feedback.rst')):
    #         self.num_feedbacks += 1
    #         self.tree[subject][assignment][group][delivery] = join(directory, 'feedback.rst')

    # def collect_data(self):
    #     # start the recursive decent into the directory tree
    #     self.collect_from_subjects(self.root_dir)


if __name__ == '__main__':
    DevilryClientStatus(*sys.argv[1:]).run()
