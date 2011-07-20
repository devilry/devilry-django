#!/usr/bin/env python

from devilryclient.utils import findconffolder, get_config
from os.path import dirname, sep, join
from os import getcwd


class DevilryClientAdd(object):
    """Mark a feedback as done and ready for upload"""

    def __init__(self):
        self.conf = get_config()
        self.root_dir = dirname(findconffolder())

    def check_context(self):
        print getcwd().replace(self.root_dir, '').split(sep)
        split_path = getcwd().replace(self.root_dir, '').split(sep)

        # 7 is the depth for deliveries:
        # <root_dir>/subject/period/assignment/assignmentgroup/deadline/delivery/
        # There should be a 'feedback.rst' at this depth
        if len(split_path) >= 7:
            print "TODO: Ok, add ", join(sep.join(split_path[0:7]), 'feedback.rst')
        else:
            print "cannot add", "'" + sep.join(split_path) + "'"

    def run(self):
        self.check_context()


if __name__ == '__main__':
    DevilryClientAdd().run()
