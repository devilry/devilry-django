from django.utils.translation import ugettext as _

from ..adminscripts.dbsanity import DbSanityCheck
from models import Feedback, Assignment, AssignmentGroup
from gradeplugin import (GradePluginDoesNotExistError,
        WrongContentTypeError, GradePluginError)


class GradepluginsSanityCheck(DbSanityCheck):
    @classmethod
    def get_label(cls):
        return _("Grade plugins")

    def check(self):
        for assignment in Assignment.objects.iterator():
            try:
                assignment.validate_gradeplugin()
            except GradePluginDoesNotExistError, e:
                self.add_fatal_error("%s: %s" % (assignment, str(e)))
        for feedback in Feedback.objects.iterator():
            try:
                feedback.validate_gradeobj()
            except GradePluginError, e:
                self.add_autofixable_error("%s: %s" % (feedback, str(e)))

    @classmethod
    def fix(cls):
        for feedback in Feedback.objects.iterator():
            try:
                feedback.validate_gradeobj()
            except GradePluginDoesNotExistError, e:
                pass # can not autofix
            except WrongContentTypeError, e:
                assignment = feedback.delivery.assignment_group.parentnode
                correct_ct = assignment.get_gradeplugin_registryitem().get_content_type()
                feedback.content_type = correct_ct
                feedback.save()


class AssignmentSanityCheck(DbSanityCheck):
    @classmethod
    def get_label(cls):
        return _("Assignment")

    def check(self):
        for assignment in Assignment.objects.iterator():
            try:
                correct_maxpoints = assignment._get_maxpoints()
            except Exception, e:
                self.add_fatal_error(
                    "Assignment %s: Could not get maxpoints from "\
                    "grade plugin. This i probably because the grade "\
                    "plugin is incorrect_maxpointsly configured" % (
                        assignment))
            else:
                if not assignment.maxpoints == correct_maxpoints:
                    self.add_autofixable_error(
                        "Assignment %s: Wrong maxpoints:"\
                        "%s. Should be: %s." % (
                            assignment, assignment.maxpoints,
                            correct_maxpoints))
                if assignment.autoscale:
                    if not assignment.pointscale == correct_maxpoints:
                        self.add_autofixable_error(
                            "Assignment %s: Wrong automatic pointscale:"\
                            "%s. Should be: %s." % (
                                assignment, assignment.pointscale,
                                correct_maxpoints))


    @classmethod
    def fix(cls):
        for assignment in Assignment.objects.iterator():
            try:
                correct_maxpoints = assignment._get_maxpoints()
            except Exception, e:
                pass #todo: handle errors
            else:
                if (assignment.maxpoints != correct_maxpoints) \
                        or (assignment.autoscale and
                                assignment.pointscale != correct_maxpoints):
                    assignment.save()


class AssignmentGroupSanityCheck(DbSanityCheck):
    @classmethod
    def get_label(cls):
        return _("AssignmentGroup")

    def check(self):
        for ag in AssignmentGroup.objects.iterator():
            correct_status = ag._get_status_from_qry()
            if ag.status != correct_status:
                self.add_autofixable_error(
                    "%s correct status:%s, current status: %s." % (
                        ag, correct_status, ag.status))
            correct_points, correct_is_passing_grade = ag._get_gradeplugin_cached_fields()
            if ag.points != correct_points:
                self.add_autofixable_error(
                    "%s correct points:%d, current points: %d." % (
                        ag, correct_points, ag.points))
            if correct_is_passing_grade != ag.is_passing_grade:
                self.add_autofixable_error(
                    "%s correct is_passing_grade:%s, "\
                    "current is_passing_grade:%s." % (
                        ag, correct_is_passing_grade, ag.is_passing_grade))

            fmt = "%.2f"
            correct_scaled_points = fmt % ag._get_scaled_points()
            scaled_points = fmt % ag.scaled_points
            if correct_scaled_points != scaled_points:
                self.add_autofixable_error(
                    "%s correct is_passing_grade:%s, "\
                    "current is_passing_grade:%s." % (
                        ag, correct_scaled_points, ag.scaled_points))

    @classmethod
    def fix(cls):
        for ag in AssignmentGroup.objects.iterator():
            ag.save() # set correct scale_points
            ag.update_gradeplugin_cached_fields()
