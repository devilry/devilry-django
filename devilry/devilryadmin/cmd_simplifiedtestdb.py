#!/usr/bin/env python
# Create simplified test DB.

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
            '--grade-maxpoints', str(a['maxpoints']),
            '--subject-long-name', subject_long_name,
            '--period-long-name', period_long_name,
            '--assignment-long-name', a['long_name']]
        call(args)



if __name__ == '__main__':
    from common import depends
    depends('init_exampledb')

    create_testgroups(
            path = 'duckburgh.univ:duck1100.h01',
            numstudents = 2, numexaminers = 1,
            subject_long_name = 'DUCK1100 - Getting started with python',
            period_long_name = 'Spring year zero',
            assignments = [
                {'shortname': 'week1', 'deadlineprofile': '-30', 'maxpoints': 14,
                    'gradeplugin': 'grade_rstschema:rstschemagrade',
                    'long_name': 'The one and only week one'},
            ])
