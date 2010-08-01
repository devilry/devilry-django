#!/usr/bin/env python

from cli import Cli, Login, Init
from examinercmd import ListAssignmentGroups, Sync, ListAssignments, \
        Feedback, InfoCmd


# TODO: make sure SESSION_COOKIE_SECURE is enabled by default or something
#       see: http://docs.djangoproject.com/en/dev/topics/http/sessions/#settings


if __name__ == '__main__':
    Cli([
        Init,
        Login,
        ListAssignments,
        ListAssignmentGroups,
        Sync,
        InfoCmd,
        Feedback]).cli()
