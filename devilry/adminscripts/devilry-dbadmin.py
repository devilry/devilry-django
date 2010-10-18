#!/usr/bin/env python

from optparse import OptionParser
import logging

from common import (setup_logging, load_devilry_plugins, add_debug_opt,
    add_quiet_opt, add_settings_option, set_django_settings_module)


extra_help = """
Actions:
    validate-gradeplugins
        Check that all grade plugins used in the database is
        available/correct.
    
    validate-gradeplugin-content-types
        AssignmentGroup objects have a grade attribute that should be a
        instance of the grade plugin of the Assignment. This that this is
        correct onchecks all AssignmentGroups.

    fix-gradeplugin-content-type-errors
        Fixes any of the errors explained in the
        <validate-gradeplugin-content-types> action.

    check-assignmentgroup-status
        We store the status of a AssignmentGroup as a number in the status
        field. This number is set by post_save events, using a query, so
        it might become corrupted over time. This action checks all these
        numbers, but changes nothing.

    set-correct-assignmentgroup-status
        Fixes the status attribute on all AssignmentGroups with wrong
        status.

    fix-grade-rstschema-points
        The restructured text grade plugin stores points in the database in
        addition to the schema each examiner submits for efficiency. This
        could get out of sync. To recalculate all, run this. Use
        grade_rstschema_check_points to check without changing anything.

    check-grade-rstschema-points
        See fix-grade-rstschema-points.
"""


p = OptionParser(
        usage = "%prog [options] <action>")
add_settings_option(p)
p.add_option("--djangoadmin-script", dest="djangoadmin",
        default='django-admin.py',
        help="Path to the django-admin.py script. Defaults to "\
            "'django-admin.py', which means that it must be on the PATH.",
            metavar="PATH")
p.add_option("--no-backup-on-restore", action="store_false",
    dest="backup_on_restore", default=True,
    help="Normally a backup is made before a restore (because restore "\
        "destroys data). Use this to skip the backup.")
add_quiet_opt(p)
add_debug_opt(p)
(opt, args) = p.parse_args()
setup_logging(opt)

# Django must be imported after setting DJANGO_SETTINGS_MODULE
set_django_settings_module(opt)
load_devilry_plugins()
from devilry.core.models import Feedback, Assignment, AssignmentGroup
from devilry.core.gradeplugin import (GradePluginDoesNotExistError,
        WrongContentTypeError, GradePluginError)
from devilry.addons.grade_rstschema.models import RstSchemaGrade


def exit_help(msg=""):
    p.print_help()
    print
    print extra_help
    raise SystemExit(msg)

def validate_gradeplugins():
    for assignment in Assignment.objects.all():
        try:
            assignment.validate_gradeplugin()
        except GradePluginDoesNotExistError, e:
            logging.error("%s: %s" % (assignment, str(e)))
        else:
            logging.debug('%-70s  [ OK ]' % assignment)

def validate_gradeplugin_contenttypes():
    for feedback in Feedback.objects.all():
        try:
            feedback.validate_gradeobj()
        except GradePluginError, e:
            logging.error("%s: %s" % (feedback, str(e)))
        else:
            logging.debug("%-70s  [ OK ]" % feedback)

def check_assignmentgroup_status():
    for ag in AssignmentGroup.objects.all():
        correct_status = ag._get_status_from_qry()
        if ag.status == correct_status:
            logging.debug("%s correct status:%s, current status: %s." % (ag,
                ag.status, correct_status))
        else:
            logging.error("%s correct status:%s, current status: %s." % (ag,
                ag.status, correct_status))

def set_correct_assignmentgroup_status():
    for ag in AssignmentGroup.objects.all():
        correct_status = ag._get_status_from_qry()
        if ag.status == correct_status:
            logging.debug("%s skipped (has correct status: %s)" % (ag,
                ag.status))
        else:
            logging.warning("%s status changed from %s to %s." % (ag,
                ag.status, correct_status))
            ag.status = correct_status
            ag.save()

def fix_grade_rstschema_points():
    for rg in RstSchemaGrade.objects.all():
        rg.save()
    logging.info("All grade_rstschema points recalculated successfully.")

def check_grade_rstschema_points():
    for rg in RstSchemaGrade.objects.all():
        feedback_obj = rg.get_feedback_obj()
        points, maxpoints = rg.get_points(feedback_obj)
        if points == rg.points and maxpoints == rg.maxpoints:
            logging.debug("%s has correct points: %s" % (rg,
                rg.get_grade_as_short_string(feedback_obj)))
        else:
            logging.warning("%s has incorrect points." % rg)


if len(args) == 0:
    exit_help()
action = args[0]

if action == "fix-gradeplugin-content-type-errors":
    for feedback in Feedback.objects.all():
        try:
            feedback.validate_gradeobj()
        except GradePluginDoesNotExistError, e:
            logging.error("%s: %s" % (feedback, str(e)))
        except WrongContentTypeError, e:
            assignment = feedback.delivery.assignment_group.parentnode
            correct_ct = assignment.get_gradeplugin_registryitem().get_content_type()
            feedback.content_type = correct_ct
            feedback.save()
            logging.warning("%-70s: Content type changed to: id: %s (%s)." % (
                feedback, correct_ct.pk, correct_ct))
        else:
            logging.debug("%-70s  [ NO CHANGE REQUIRED ]" % feedback)

elif action == "validate-gradeplugins":
    validate_gradeplugins()
elif action == "validate-gradeplugin-content-types":
    validate_gradeplugin_contenttypes()
elif action == "check-assignmentgroup-status":
    check_assignmentgroup_status()
elif action == "set-correct-assignmentgroup-status":
    set_correct_assignmentgroup_status()
elif action == "fix-grade-rstschema-points":
    fix_grade_rstschema_points()
elif action == "check-grade-rstschema-points":
    check_grade_rstschema_points()
else:
    exit_help("ERROR: Invalid action.")
