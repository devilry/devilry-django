from django.utils.translation import ugettext as _

from devilry.adminscripts.dbsanity import DbSanityCheck
from models import Feedback, Assignment, AssignmentGroup
from gradeplugin import (GradePluginDoesNotExistError,
        WrongContentTypeError, GradePluginError)


class GradepluginsSanityCheck(DbSanityCheck):
    @classmethod
    def get_label(cls):
        return _("Grade plugins")

    def check(self):
        for assignment in Assignment.objects.all():
            try:
                assignment.validate_gradeplugin()
            except GradePluginDoesNotExistError, e:
                self.add_fatal_error("%s: %s" % (assignment, str(e)))
        for feedback in Feedback.objects.all():
            try:
                feedback.validate_gradeobj()
            except GradePluginError, e:
                self.add_autofixable_error("%s: %s" % (feedback, str(e)))

    @classmethod
    def fix(cls):
        for feedback in Feedback.objects.all():
            try:
                feedback.validate_gradeobj()
            except GradePluginDoesNotExistError, e:
                pass # can not autofix
            except WrongContentTypeError, e:
                assignment = feedback.delivery.assignment_group.parentnode
                correct_ct = assignment.get_gradeplugin_registryitem().get_content_type()
                feedback.content_type = correct_ct
                feedback.save()


class AssignmentGroupSanityCheck(DbSanityCheck):
    @classmethod
    def get_label(cls):
        return _("AssignmentGroup")

    def check(self):
        for ag in AssignmentGroup.objects.all():
            correct_status = ag._get_status_from_qry()
            if ag.status != correct_status:
                self.add_autofixable_error(
                    "%s correct status:%s, current status: %s." % (
                        ag, correct_status, ag.status))
            correct_points = ag._find_points()
            if ag.points != correct_points:
                self.add_autofixable_error(
                    "%s correct points:%d, current points: %d." % (
                        ag, correct_points, ag.points))

    @classmethod
    def fix(cls):
        for ag in AssignmentGroup.objects.all():
            correct_status = ag._get_status_from_qry()
            if ag.status != correct_status:
                ag.status = correct_status
                ag.save()
            correct_points = ag._find_points()
            if ag.points != correct_points:
                ag.points = correct_points
                ag.save()
