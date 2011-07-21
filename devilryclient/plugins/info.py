#!/usr/bin/env python

from devilryclient.utils import findconffolder, get_config, get_metadata_from_path
from os.path import dirname, sep, join, exists
from os import getcwd
from datetime import datetime, timedelta


class DevilryClientInfo(object):

    def __init__(self):
        self.conf = get_config()
        self.root_dir = dirname(findconffolder())
        f = open(join(findconffolder(), 'metadata'), 'r')
        self.metadata = eval(f.read())

    def check_context(self):
        self.split_path = getcwd().replace(self.root_dir, '').split(sep)

        context = {
            1: self.root,
            2: self.subject,
            3: self.period,
            4: self.assignment,
            5: self.assignmentgroup,
            6: self.deadline,
            7: self.delivery,
            }.get(len(self.split_path), self.delivery)

        # if we go any deeper than to the delivery folder, show info
        # about the delivery, instead of failing and show nothing
        if context == self.delivery:
            self.split_path = self.split_path[0:7]

        self.subtree = get_metadata_from_path(sep.join(self.split_path))
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
        print "# Deadline info"
        print "#"
        print "# Exipres in: {time}".format(time=self.subtree['.meta'].get('deadline', -1))

    def delivery(self):
        print "# Delivery info (TODO: format better, align stuff)"
        print "#"
        print "# Delivered by: ", self.subtree['.meta'].get('delivered_by', "FixMe")
        print "# Corrected: {bool}".format(bool='Yes' if self.subtree['.meta'].get('done', False) else 'No')
        print "# Number of files: ", self.subtree['.meta'].get('num_files', "FixMe")
        for idx, f in enumerate(self.subtree['files'], 1):
            print "#   {idx}: {fname} ({size})".format(idx=idx, fname=f, size='FixMe bytes')

        if exists(join(self.root_dir, sep.join(self.split_path[1:7]), 'feedback')):
            print "#"
            print "# Feedback"
            print "#   This delivery contains a feedback. Show some info about it"

    def run(self):
        self.check_context()


if __name__ == '__main__':
    DevilryClientInfo().run()
