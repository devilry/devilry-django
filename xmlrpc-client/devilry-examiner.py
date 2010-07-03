#!/usr/bin/env python

from utils import Cli
from commoncmd import Login, Init
from examinercmd import ListAssignmentGroups, Sync, ListAssignments, \
        Feedback


# TODO: make sure SESSION_COOKIE_SECURE is enabled by default or something
#       see: http://docs.djangoproject.com/en/dev/topics/http/sessions/#settings


if __name__ == '__main__':
    c = Cli()
    for action in (
            Init,
            Login,
            ListAssignments,
            ListAssignmentGroups,
            Sync,
            Feedback):
        c.add_command(action)
    c.cli()
