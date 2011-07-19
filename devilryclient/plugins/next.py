#!/usr/bin/env python

from devilryclient.utils import findconffolder
from os.path import dirname, join, exists
from os import listdir, chdir, getcwd


class DevilryClientNext(object):
    """
    Update the 'next' symlink in the root folder of the workspace

    Search through the hierachy for deliveries that have no feedback,
    and create a symlink to it
    """

    def __init__(self):
        self.conf_dir = findconffolder()
        self.root_dir = dirname(self.conf_dir)

    def done_with_current(self):
        """
        Check if the current link is done, or even exists.

        Return True if the link doesn't exist, or if the current
        delivery has been added or pushed to the server.
        """

        # change the working directory to root_dir
        chdir(self.root_dir)

        current_link = join(getcwd(), 'current')
        if not exists(current_link):
            return True

        # This needs to be checked in an other way. We should have a
        # file containing some meta-data that says if the feedback has
        # been pushed to the server, or is already published
        if exists(join(current_link, 'feedback.rst')):
            return True

        return False

    def find_next(self):
        """
        Search for a delivery without a feedback.rst in it
        """
        pass
