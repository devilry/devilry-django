from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from devilry.apps.core.models import RelatedStudent
from devilry.devilry_account.models import User


class Candidate(models.Model):
    """
    .. attribute:: assignment_group

        The `AssignmentGroup`_ where this groups belongs.

    .. attribute:: student

        A student (a foreign key to a User).

    .. attribute:: candidate_id

        A optional candidate id. This can be anything as long as it is not
        more than 30 characters. When the assignment is anonymous, this is
        the "name" shown to examiners instead of the username of the
        student.
    """

    class Meta:
        app_label = 'core'

    student = models.ForeignKey(User)
    relatedstudent = models.ForeignKey(RelatedStudent,
                                       null=True, default=None, blank=True)

    assignment_group = models.ForeignKey(
        'AssignmentGroup',
        related_name='candidates')
    candidate_id = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='An optional candidate id. This can be anything as long as it '
                  'is less than 30 characters. Used to show the user on anonymous assignmens.')
    automatic_anonymous_id = models.CharField(
        max_length=255, blank=True, null=False, default='',
        help_text='An automatically generated anonymous ID.')

    def __unicode__(self):
        return 'Candiate id={id}, student={student}, group={group}'.format(
            id=self.id,
            student=self.student,
            group=self.assignment_group)

    def get_student_displayname(self):
        return self.student.get_full_name()

    def get_anonymous_displayname(self):
        return self.candidate_id or self.automatic_anonymous_id or _('Anonymous ID missing')
