#!/usr/bin/env python

from devilryclient.utils import findconffolder, get_config
from os.path import dirname, sep, join
from os import getcwd


class DevilryClientInfo(object):

    def __init__(self):
        self.conf = get_config()
        self.root_dir = dirname(findconffolder())
        f = open(join(findconffolder(), 'metadata'), 'r')
        self.metadata = eval(f.read())

    def check_context(self):
        self.split_path = getcwd().replace(self.root_dir, '').split(sep)
        {
            1: self.root,
            2: self.subject,
            3: self.period,
            4: self.assignment,
            5: self.assignmentgroup,
            6: self.deadline,
            7: self.delivery,
            8: self.feedback,
            }.get(len(self.split_path), self.default)()

    def root(self):
        print "This is the root folder"
        for key, val in self.metadata.items():
            print key

    def subject(self):
        print ""
        print "This is the root folder"
        for key, val in self.metadata.items():
            print key

    def period(self):
        print "Info about period"
        for key, val in self.metadata.items():
            print key

    def assignment(self):
        print "Info about assignment"
        for key, val in self.metadata.items():
            print key

    def assignmentgroup(self):
        print "Info about assignmentgroup"
        for key, val in self.metadata.items():
            print key

    def deadline(self):
        print "Info about deadline"
        for key, val in self.metadata.items():
            print key

    def delivery(self):
        print "Info about delivery"
        for key, val in self.metadata.items():
            print key

    def feedback(self):
        print "Info about feedback"
        for key, val in self.metadata.items():
            print key

    def default(self):
        print "Error case"

    def run(self):
        self.check_context()


if __name__ == '__main__':
    DevilryClientInfo().run()
