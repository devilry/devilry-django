#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    DJANGOENV = os.environ.get('DJANGOENV', 'develop')

    if DJANGOENV == 'develop': # Used for local development
        from devilry_developer.settings.develop import *
    elif DJANGOENV == 'test': # Used when running the Django tests
        from devilry_developer.settings.test import *
    else:
        raise ValueError('Invalid value for the DJANGOENV environment variable: {}'.format(DJANGOENV))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
