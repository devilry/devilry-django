#!/usr/bin/env python

from optparse import OptionParser
import logging
import itertools
from random import randint
from datetime import datetime, timedelta

from devilry.apps.gradeeditors.models import Config
from common import (setup_logging, load_devilry_plugins,
    add_settings_option, set_django_settings_module, add_quiet_opt,
    add_debug_opt)



if __name__ == "__main__":

    p = OptionParser(
            usage = "%prog [options] <assignment-path>")
    add_settings_option(p)
    p.add_option("-s", "--num-students", dest="num_students",
            default=50, type='int',
            help="Number of students. Defaults to 10.")
    p.add_option("-e", "--num-examiners", dest="num_examiners",
            default=3, type='int',
            help="Number of examiners. Defaults to 3.")
    p.add_option("--groupname-prefix", dest="groupname_prefix",
            default=None,
            help="Group name prefix. Group names will be this prefix plus "\
                    "a number. If you dont specify this, group name will "\
                    "be blank.")
    p.add_option("--subject-long-name", dest="subject_long_name",
            default=None,
            help="The long name of the subject. Defaults to short name"\
                "capitalized")
    p.add_option("--period-long-name", dest="period_long_name",
            default=None,
            help="The long name of the period. Defaults to short name"\
                "capitalized")
    p.add_option("--assignment-long-name", dest="assignment_long_name",
            default=None,
            help="The long name of the assignment. Defaults to short name"\
                "capitalized")
    p.add_option("--student-name-prefix", dest="studentname_prefix",
            default="student",
            help="Student name prefix. Student names will be this prefix "\
                    "plus a number. Defaults to 'student'")
    p.add_option("--students-per-group", dest="students_per_group",
            default=1, type='int',
            help="Number of students per group. Defaults to 1.")
    p.add_option("--examiner-name-prefix", dest="examinername_prefix",
            default="examiner",
            help="Examiner name prefix. Examiner names will be this prefix "\
                    "plus a number. Defaults to 'examiner'")
    p.add_option("--examiners-per-group", dest="examiners_per_group",
            default=1, type='int',
            help="Number of examiners per group. Defaults to 1.")
    p.add_option("-g", "--grade-maxpoints", dest="grade_maxpoints",
            default=1, type='int',
            help="Maximum number of points possible on the assignment. "\
                "Groups will get a random score between 0 and this number. "
                "Defaults to 1.")
    p.add_option("--pointscale", dest="pointscale",
            default=None, type='int',
            help="The pointscale of the assignment. Default is "\
                    "no pointscale.")
    p.add_option("--deliverycountrange", default='0-4',
                 dest='deliverycountrange',
                 help=("Number of deliveries. If it is a range separated by '-', "
                       "a random number of deliveries in this range is used. Defaults "
                       "to '0-4'"))
    p.add_option("--grade-plugin", dest="gradeplugin",
            default=None, help="Grade plugin key.")
    p.add_option("-p", "--deadline-profile", dest="deadline_profiles",
            default='-10',
            help="Deadline profile. Defaults to '-10'")


    add_quiet_opt(p)
    add_debug_opt(p)
    (opt, args) = p.parse_args()
    setup_logging(opt)

    # Django must be imported after setting DJANGO_SETTINGS_MODULE
    set_django_settings_module(opt)
    load_devilry_plugins()
    from django.contrib.auth.models import User
    from devilry.apps.core.models import Delivery
    from devilry.apps.core.testhelpers import create_from_path

    def exit_help():
        p.print_help()
        raise SystemExit()
    if len(args) != 1:
        exit_help()
    setup_logging(opt)


    from devilry.devilryadmin.create_random_exampledata import create_example_assignment
    create_example_assignment(args[0],
                              assignment_long_name = opt.assignment_long_name,
                              pointscale = opt.pointscale,
                              subject_long_name = opt.subject_long_name,
                              period_long_name = opt.period_long_name,

                              groupname_prefix = opt.groupname_prefix,
                              deadline_profiles = opt.deadline_profiles,

                              num_students = opt.num_students,
                              studentname_prefix = opt.studentname_prefix,
                              students_per_group = opt.students_per_group,

                              num_examiners = opt.num_examiners,
                              examinername_prefix = opt.examinername_prefix,
                              examiners_per_group = opt.examiners_per_group,

                              grade_maxpoints = opt.grade_maxpoints,
                              deliverycountrange = opt.deliverycountrange)
