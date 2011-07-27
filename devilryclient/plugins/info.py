#!/usr/bin/env python

from devilryclient.utils import findconffolder, get_config
from os.path import dirname, sep, join, exists
from os import getcwd
from datetime import datetime, timedelta


class DevilryClientInfo(object):

    def __init__(self):
        self.conf = get_config()
        self.root_dir = dirname(findconffolder()) + sep
        f = open(join(findconffolder(), 'metadata'), 'r')
        self.metadata = eval(f.read())

    def check_context(self):
        self.split_path = (getcwd() + sep).replace(self.root_dir, '').split(sep)[:-1]

        context = {
            0: self.root,
            1: self.subject,
            2: self.period,
            3: self.assignment,
            4: self.assignmentgroup,
            5: self.deadline,
            6: self.delivery,
            }.get(len(self.split_path), self.delivery)

        # if we go any deeper than to the delivery folder, show info
        # about the delivery, instead of failing and show nothing
        print (getcwd() + sep).replace(self.root_dir, '')
        if context == self.delivery:
            self.split_path = self.split_path[0:6]
        print self.split_path

        if len(self.split_path) != 0:
            self.subtree = self.metadata[sep.join(self.split_path)]

        context()
        print "#"

    def root(self):
        print "This is the root folder. Just call status.py, maybe?"

    def subject(self):
        print "subject"

    def period(self):
        print "period"

    def assignment(self):
        print "assignment"

    def assignmentgroup(self):
        print "assignmentgroup"

    def deadline(self):
        """
        Displays information about the deadline the user is currently in.
        """

        print "# Deadline info"
        print "#"
        print "# Exipres in: {time}".format(time=self.subtree['.meta'].get('deadline', -1))

    def delivery(self):
        """
        Displays information about the delivery the user is currently in.
        """

        print "# Delivery info (TODO: format better, align stuff)"
        print "#"
        print "# Delivered by: ", self.subtree['.meta'].get('delivered_by', "FixMe")
        print "# Corrected: {bool}".format(bool='Yes' if self.subtree['.meta'].get('done', False) else 'No')
        print "# Number of files: ", self.subtree['.meta'].get('num_files', "FixMe")
        for idx, f in enumerate(self.subtree['files'], 1):
            print "#   {idx}: {fname} ({size})".format(idx=idx, fname=f, size='FixMe bytes')

        if exists(join(self.root_dir, sep.join(self.split_path[0:6]), 'feedback')):
            print "#"
            print "# Feedback"
            print "#   This delivery contains a feedback. Show some info about it"

    def run(self):
        self.check_context()


if __name__ == '__main__':
    DevilryClientInfo().run()
