#!/usr/bin/env python
from devilryclient.utils import findconffolder, get_config, get_metadata
from os.path import dirname, join, sep, exists
from os import listdir


class DevilryClientUpdateMeta(object):

    def __init__(self):
        self.conf = get_config()
        self.root_dir = dirname(findconffolder())
        self.metadata = get_metadata()

    def run(self):
        #self.collect_data()
        for key in self.metadata.keys():
            print key

if __name__ == '__main__':
    DevilryClientUpdateMeta().run()
