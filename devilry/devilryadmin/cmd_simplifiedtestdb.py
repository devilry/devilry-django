    #!/usr/bin/env python
# Create simplified test DB.

#################################################################
# WARNING: DO NOT CHANGE this file lightly. The resulting
# database is used to generate the simplifed fixture,
# which is used in many tests.
#################################################################

from sys import exit
from os.path import join
import logging

from common import (getscriptsdir, require_djangoproject,
                    depends, Command,
                    DevilryAdmArgumentParser)
from django.contrib.auth.models import User
from create_random_exampledata import create_example_assignment
from devilry.apps.core.testhelper import TestHelper
from devilry.apps.core import models


parser = DevilryAdmArgumentParser(description='Process some integers.')
parser.add_argument('-s', '--num_students', type=int, default=2,
                    help='Number of students on each assignment (defaults to 2).')
parser.add_argument('-e', '--num_examiners', type=int, default=1,
                    help='Number of examiners on each assignment (defaults to 1).')
parser.add_argument('-d', '--duckburghusers', action='store_true',
                    help='Load duckburgh users.')
parser.add_argument("--deliverycountrange", default='0-4',
                    help=("Number of deliveries. If it is a range separated by '-', "
                          "a random number of deliveries in this range is used. Defaults "
                          "to '0-4'"))
parser.add_argument('--completionlist', action='store_true',
                   help='Print completionlist for bash completion.')
args = parser.parse_args()

if args.completionlist:
    print "--num_students --num_examiners --duckburghusers --deliverycountrange"
    exit(0)


require_djangoproject()
depends(Command('init_exampledb'),
        Command('load_grandmauser'))
if args.duckburghusers:
    depends(Command('load_duckburghusers'))

logging.basicConfig(level=logging.INFO, format='%(levelname)7s: %(message)s')






scriptsdir = getscriptsdir()
create_testgroups_cmd = join(scriptsdir, 'create_testgroups.py')

def create_testgroups(period, assignments, **shared_kwargs):
    logging.info(str(period))
    for kwargs in assignments:
        kw = dict()
        kw.update(shared_kwargs)
        kw.update(kwargs)
        create_example_assignment(period, **kw)


def add_extra_relatedusers(period):
    for username in ('huey', 'dewey', 'louie', 'april', 'may', 'june'):
        models.RelatedStudent.objects.create(user=User.objects.get(username=username), period=period)


testhelper = TestHelper()
testhelper.add()
testhelper.add(nodes='duckburgh.univ:admin(duckburghboss)',
               subjects=['duck1100:admin(donald):ln(DUCK1100 - Getting started with python)',
                         'duck1080:admin(daisy):ln(DUCK1080 - Making the illogical seem logical)',
                         'duck3580:admin(clarabelle):ln(DUCK3580 - Making the web work)',
                         'duck5063:admin(scrooge):ln(DUCK5063 - Make low level stuff - avoiding permanent psychological scarring of most of the students)'],
               periods=['spring01:admin(fethry,gus,gladstone):ln(Spring year zero)'])
testhelper.add(nodes='duckburgh.highschool')
testhelper.add(nodes='metropolis')
testhelper.add(nodes='arkhamcity.college')

if args.duckburghusers:
    add_extra_relatedusers(testhelper.duck1100_spring01)

# Duck 1100
create_testgroups(testhelper.duck1100_spring01,
                  num_students = args.num_students, num_examiners = args.num_examiners,
                  deliverycountrange=args.deliverycountrange,
                  assignments = [
                                 {'short_name': 'week1', 'deadline_profiles': '-60', 'grade_maxpoints': 14,
                                  'long_name': 'The one and only week one'},
                                 {'short_name': 'week2', 'deadline_profiles': '-30', 'grade_maxpoints': 10,
                                  'long_name': 'The one and only week two'},
                                 {'short_name': 'week3', 'deadline_profiles': '-9', 'grade_maxpoints': 9,
                                  'long_name': 'The one and only week tree'},
                                ])
create_testgroups(testhelper.duck1100_spring01,
                  num_students = args.num_students/3, num_examiners = args.num_examiners,
                  deliverycountrange=args.deliverycountrange,
                  assignments = [
                                 {'short_name': 'project1', 'deadline_profiles': '-60', 'grade_maxpoints': 60,
                                  'long_name': 'The easy project'},
                                 {'short_name': 'project2', 'deadline_profiles': '-3', 'grade_maxpoints': 100,
                                  'long_name': 'The hard project'},
                                ])

create_testgroups(testhelper.duck1100_spring01,
                  num_students = args.num_students + 5, num_examiners = args.num_examiners,
                  deliverycountrange=args.deliverycountrange,
                  assignments = [
                                 {'short_name': 'extra', 'deadline_profiles': '-20', 'grade_maxpoints': 5,
                                  'long_name': 'Extra'},
                                ])


# Duck 1080
create_testgroups(testhelper.duck1080_spring01,
                  num_students = args.num_students, num_examiners = args.num_examiners,
                  deliverycountrange=args.deliverycountrange,
                  assignments = [
                                 {'short_name': 'week1', 'deadline_profiles': '-30', 'grade_maxpoints': 11,
                                  'long_name': 'The one and only week one'},
                                 {'short_name': 'week2', 'deadline_profiles': '-20', 'grade_maxpoints': 10,
                                  'long_name': 'The one and only week two'},
                                 {'short_name': 'week3', 'deadline_profiles': '-3', 'grade_maxpoints': 9,
                                  'long_name': 'The one and only week tree'},
                                ])

# Duck 3580
create_testgroups(testhelper.duck3580_spring01,
                  num_students = args.num_students, num_examiners = args.num_examiners,
                  deliverycountrange=args.deliverycountrange,
                  assignments = [
                                 {'short_name': 'week1', 'deadline_profiles': '-40,-30,-20',
                                  'long_name': 'Week one'},
                                 {'short_name': 'week2', 'deadline_profiles': '-3,-10,-20',
                                  'long_name': 'Week two'}
                                ])

# Duck 5063
create_testgroups(testhelper.duck5063_spring01,
                  num_students = args.num_students, num_examiners = args.num_examiners,
                  deliverycountrange=args.deliverycountrange,
                  assignments = [
                                 {'short_name': 'first_assignment', 'deadline_profiles': '-30',
                                  'long_name': 'First assignment'},
                                 {'short_name': 'second_assignment', 'deadline_profiles': '-3',
                                  'long_name': 'Second assignment'}
                                ],
                 students_per_group = 2, examiners_per_group = 3)


print
print "**********************************************************"
print "Create an example database"
print
print "Log in as:"
print "     - grandma    (a superadmin)"
print "     - examiner0  (an examiner)"
print "     - student0   (a student)."
print
print "Every user has password: test"
print "**********************************************************"
