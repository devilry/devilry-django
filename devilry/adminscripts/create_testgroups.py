from optparse import OptionParser
import logging

from common import (setup_logging, load_devilry_plugins,
    add_settings_option, set_django_settings_module, add_quiet_opt,
    add_debug_opt)


p = OptionParser(
        usage = "%prog [options] <assignment-id>")
add_settings_option(p)
add_quiet_opt(p)
add_debug_opt(p)
(opt, args) = p.parse_args()
setup_logging(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
set_django_settings_module(opt)
load_devilry_plugins()
from devilry.core.models import Assignment, AssignmentGroup
from django.conf import settings
from django.contrib.auth.models import User

print settings.DATABASE_NAME

def exit_help():
    p.print_help()
    raise SystemExit()
if len(args) != 1:
    exit_help()
setup_logging(opt)


assignment_id = int(args[0])
students = ['stud%d' % d for d in xrange(1,30)]
assignment = Assignment.objects.get(id=assignment_id)
print assignment
for username in students:
    student = User.objects.get(username=username)
    g = assignment.assignmentgroups.create()
    g.candidates.create(student=student)
    print g
    g.save()
