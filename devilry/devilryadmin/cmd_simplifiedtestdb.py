#!/usr/bin/env python
# Create simplified test DB.

#################################################################
# WARNING: DO NOT CHANGE this file lightly. The resulting
# database is used to generate the simplifed.json fixture,
# which is used in many tests.
#################################################################

from subprocess import call
from os.path import join
from common import getscriptsdir

scriptsdir = getscriptsdir()
create_testgroups_cmd = join(scriptsdir, 'create_testgroups.py')

def create_testgroups(
        path, numstudents, numexaminers,
        subject_long_name, period_long_name,
        assignments):
    for a in assignments:
        args = [create_testgroups_cmd,
            '{0}.{1}'.format(path, a['shortname']),
            '--grade-plugin', a['gradeplugin'],
            '--num-students', str(numstudents),
            '--num-examiners', str(numexaminers),
            '--deadline-profile', str(a['deadlineprofile']),
            '--subject-long-name', subject_long_name,
            '--period-long-name', period_long_name,
            '--assignment-long-name', a['long_name']]
        if 'maxpoints' in a:
            args.extend(['--grade-maxpoints', str(a['maxpoints'])])
        if 'pointscale' in a:
            args.extend(['--pointscale', str(a['pointscale'])])
        call(args)



if __name__ == '__main__':
    from common import depends
    depends('init_exampledb')

    # Duck 1100
    create_testgroups(
            path = 'duckburgh.univ:duck1100.spring01',
            numstudents = 2, numexaminers = 1,
            subject_long_name = 'DUCK1100 - Getting started with python',
            period_long_name = 'Spring year zero',
            assignments = [
                {'shortname': 'week1', 'deadlineprofile': '-30', 'maxpoints': 14,
                    'gradeplugin': 'grade_rstschema:rstschemagrade',
                    'long_name': 'The one and only week one'},
                {'shortname': 'week2', 'deadlineprofile': '-20', 'maxpoints': 10,
                    'gradeplugin': 'grade_rstschema:rstschemagrade',
                    'long_name': 'The one and only week two'},
                {'shortname': 'week3', 'deadlineprofile': 'old', 'maxpoints': 9,
                    'gradeplugin': 'grade_rstschema:rstschemagrade',
                    'long_name': 'The one and only week tree'},
                {'shortname': 'week4', 'deadlineprofile': 'recent', 'maxpoints': 9,
                    'gradeplugin': 'grade_rstschema:rstschemagrade',
                    'long_name': 'The one and only week tree'},
            ])

    # Duck 1080
    create_testgroups(
            path = 'duckburgh.univ:duck1080.fall01',
            numstudents = 2, numexaminers = 1,
            subject_long_name = 'DUCK1080 - Making the illogical seem logical',
            period_long_name = 'Fall year zero',
            assignments = [
                {'shortname': 'week1', 'deadlineprofile': '-30', 'maxpoints': 11,
                    'gradeplugin': 'grade_rstschema:rstschemagrade',
                    'pointscale': 10,
                    'long_name': 'The one and only week one'},
                {'shortname': 'week2', 'deadlineprofile': '-20', 'maxpoints': 10,
                    'gradeplugin': 'grade_rstschema:rstschemagrade',
                    'pointscale': 10,
                    'long_name': 'The one and only week two'},
                {'shortname': 'week3', 'deadlineprofile': 'recent', 'maxpoints': 9,
                    'gradeplugin': 'grade_rstschema:rstschemagrade',
                    'pointscale': 10,
                    'long_name': 'The one and only week tree'},
            ])

    # Duck 3580
    create_testgroups(
            path = 'duckburgh.univ:duck3580.fall01',
            numstudents = 2, numexaminers = 1,
            subject_long_name = 'DUCK3580 - Making the web work',
            period_long_name = 'Fall year zero',
            assignments = [
                {'shortname': 'week1', 'deadlineprofile': '-30',
                    'gradeplugin': 'grade_approved:approvedgrade',
                    'long_name': 'Week one'},
                {'shortname': 'week2', 'deadlineprofile': 'recent',
                    'gradeplugin': 'grade_approved:approvedgrade',
                    'long_name': 'Week two'}
            ])
