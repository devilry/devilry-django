#!/usr/bin/env python

from devilryclient.utils import findconffolder
from os.path import dirname, join
from os import getcwd
from ConfigParser import ConfigParser
from urlparse import urljoin
from subprocess import call


class DevilryClientOpen(object):

    def __init__(self):
        self.conf_dir = findconffolder()
        self.root_dir = dirname(self.conf_dir)
        self.conf = ConfigParser()
        self.conf.read(join(self.conf_dir, 'config'))
        self.server = self.conf.get('resources', 'url')

    def open(self):
        context = getcwd().replace(self.root_dir, '')
        url = urljoin(self.server, context)

        # TODO: if on macos, use 'open'
        # TODO: if on windows, use 'start', with som shuffling of the
        # arguments
        cmd = 'xdg-opensdf'
        try:
            call([cmd, url])
        except OSError:
            print "Unable to run program: {cmd}".format(cmd=cmd)
            print "URL for current context: {url}".format(url=url)

    def run(self):
        self.open()


if __name__ == '__main__':
    DevilryClientOpen().run()
