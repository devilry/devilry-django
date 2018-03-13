from __future__ import unicode_literals
import os
from datetime import datetime

"""
How to use this script
======================

Put this on the server. Recommented location:

    <directory that contains manage.py>/custom_debugging_scripts/student_frontpage_query_debug.py

Update DJANGO_SETTINGS_MODULE and username variables below.

Run it with:

    $ venv/bin/python custom_debugging_scripts/student_frontpage_query_debug.py
"""


if __name__ == '__main__':  # Wrap it in main to be absolutely sure that this is not auto-executed by an import somehow

    # Change this to reflect the value for DJANGO_SETTINGS_MODULE in your manage.py
    DJANGO_SETTINGS_MODULE = 'devilry.project.settingsproxy'

    # Change this to the username you want to test
    username = 'dewey'

    # Do not touch this
    os.environ['DJANGO_SETTINGS_MODULE'] = DJANGO_SETTINGS_MODULE
    from devilry.apps.core.models import *
    from django.contrib.auth import get_user_model


    def print_frontpage_group_info(group):
        print '*' * 70
        print '{} - {} - {}'.format(
            group.subject.long_name,
            group.period.long_name,
            group.assignment.long_name
        ).encode('utf-8')
        print '  Deadline:', group.last_deadline_datetime
        print '  Deadline is expired:', group.last_deadline_datetime < datetime.now()


    def print_frontpage_query_results(user):
        groups = AssignmentGroup.objects.filter_student_has_access(user) \
            .filter_is_active() \
            .filter_can_add_deliveries() \
            .annotate_with_last_deadline_datetime() \
            .extra(order_by=['last_deadline_datetime'])
        for group in groups:
            print_frontpage_group_info(group=group)

    print_frontpage_query_results(user=get_user_model().objects.get(username=username))
