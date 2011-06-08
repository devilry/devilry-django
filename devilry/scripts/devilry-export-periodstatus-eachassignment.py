#!/usr/bin/env python

from optparse import OptionParser
import logging

from common import (setup_logging, load_devilry_plugins,
    add_settings_option, set_django_settings_module, add_quiet_opt,
    add_debug_opt)


p = OptionParser(
        usage = "%prog [options] <Subject short name> <Period short name>")
add_settings_option(p)
add_quiet_opt(p)
add_debug_opt(p)
(opt, args) = p.parse_args()
setup_logging(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
set_django_settings_module(opt)
from django.contrib.auth.models import User
from devilry.apps.core.models import Period

def exit_help():
    p.print_help()
    raise SystemExit()
if len(args) != 2:
    exit_help()
setup_logging(opt)

subject_short_name, period_short_name = args



period = Period.objects.get(short_name=period_short_name,
        parentnode__short_name=subject_short_name)
users = User.objects.filter(
    candidate__assignment_group__parentnode__parentnode=period).distinct()


for assignment in period.assignments.all():
    for group in assignment.assignmentgroups.all():
        for candidate in group.candidates.all():
            print "%s;%s;%s;%s;%s" % (
                    subject_short_name.upper(),
                    period_short_name,
                    assignment.short_name,
                    candidate.student.username,
                    group.is_passing_grade)

#for user in users:
    #for assignment in period.assignments:
        #if student in assignment
    #print "%s;%s;%s" % (
            #subject_short_name.upper(),
            #user.username,
            #period.student_passes_period(user))
