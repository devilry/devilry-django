#!/usr/bin/env python

from devilryclient.utils import findconffolder, get_config, get_metadata
from os.path import dirname, sep, join
from os import getcwd


class DevilryClientAdd(object):
    """Mark a feedback as done and ready for upload"""

    def __init__(self):
        self.conf = get_config()
        self.root_dir = dirname(findconffolder())
        self.metadata = get_metadata()

    def check_context(self):
        #print getcwd().replace(self.root_dir, '').split(sep)
        split_path = getcwd().replace(self.root_dir, '').split(sep)

        # 7 is the depth for deliveries:
        # <root_dir>/subject/period/assignment/assignmentgroup/deadline/delivery/
        # There should be a 'feedback.rst' at this depth
        if len(split_path) < 7:
            print "cannot add", "'" + sep.join(split_path) + "'"
            return

        # TODO: check if there's a feedback somehow, i.eg
        # join(sep.join(split_path[0:7]), 'feedback.rst')

        # alias split_path to something shorter
        p = split_path
        if 'done' in self.metadata[p[1]][p[2]][p[3]][p[4]][p[5]][p[6]]['.meta'].keys() \
                and self.metadata[p[1]][p[2]][p[3]][p[4]][p[5]][p[6]]['.meta']['done']:
            print "Already added"
            return

        self.metadata[p[1]][p[2]][p[3]][p[4]][p[5]][p[6]]['.meta']['done'] = True
        print "Added"

    def run(self):
        self.check_context()


if __name__ == '__main__':
    DevilryClientAdd().run()
