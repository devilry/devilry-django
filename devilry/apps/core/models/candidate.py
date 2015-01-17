from django.contrib.auth.models import User
from django.db import models


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
    assignment_group = models.ForeignKey(
        'AssignmentGroup',
        related_name='candidates')
    candidate_id = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='An optional candidate id. This can be anything as long as it '
                  'is less than 30 characters. Used to show the user on anonymous assignmens.')

    def __unicode__(self):
        return 'Candiate id={id}, student={student}, group={group}'.format(
            id=self.id,
            student=self.student,
            group=self.assignment_group)

    def get_student_displayname(self):
        return self.student.devilryuserprofile.get_displayname()
