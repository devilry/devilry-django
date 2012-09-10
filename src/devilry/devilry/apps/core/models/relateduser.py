import re

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from period import Period
from node import Node
from abstract_is_admin import AbstractIsAdmin
from abstract_applicationkeyvalue import AbstractApplicationKeyValue



class RelatedUserBase(models.Model, AbstractIsAdmin):
    """
    Common fields for examiners and students related to a period.

    .. attribute:: period

        The period that the user is related to.

    .. attribute:: user

        A django.contrib.auth.models.User_ object. Must be unique within this
        period.

    .. attribute:: tags

        Comma-separated list of tags. Each tag is a word with the following
        letters allowed: a-z and 0-9. Each word is separated by a comma, and no
        whitespace.
    """
    period = models.ForeignKey(Period,
                               verbose_name='Period',
                               help_text="The period.")
    user = models.ForeignKey(User, help_text="The related user.")
    tags = models.TextField(blank=True, null=True, help_text="Comma-separated list of tags. Each tag is a word with the following letters allowed: a-z, 0-9, ``_`` and ``-``. Each word is separated by a comma, and no whitespace.")

    tags_patt = re.compile('^(?:[a-z0-9_-]+,)*[a-z0-9_-]+$')

    class Meta:
        abstract = True # This model will then not be used to create any database table. Instead, when it is used as a base class for other models, its fields will be added to those of the child class.
        unique_together = ('period', 'user')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(period__admins=user_obj) | \
                Q(period__parentnode__admins=user_obj) | \
                Q(period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def clean(self):
        if self.tags and not self.tags_patt.match(self.tags):
            raise ValidationError('tags must be a comma-separated list of tags, each tag only containing a-z, 0-9, ``_`` and ``-``.')

    def __unicode__(self):
        return '{0}:user={1}:tags={2}'.format(self.period, self.user.username, self.tags)


class RelatedExaminer(RelatedUserBase):
    """ Related examiner.

    Adds no fields to RelatedUserBase.
    """

class RelatedStudent(RelatedUserBase):
    """ Related student.

    .. attribute:: candidate_id

        If a candidate has the same Candidate ID for all or many assignments in
        a semester, this field can be set to simplify setting candidate IDs on
        each assignment.
    """
    candidate_id = models.CharField(max_length=30, blank=True, null=True,
                                    help_text="If a candidate has the same Candidate ID for all or many assignments in a semester, this field can be set to simplify setting candidate IDs on each assignment.")

    def __unicode__(self):
        return '{0}:candidate_id={1}'.format(super(RelatedStudent, self).__unicode__(), self.candidate_id)


class RelatedStudentKeyValue(AbstractApplicationKeyValue, AbstractIsAdmin):
    """ Key/value pair tied to a specific RelatedStudent. """
    relatedstudent = models.ForeignKey(RelatedStudent)
    student_can_read = models.BooleanField(help_text='Specifies if a student can read the value or not.')

    class Meta:
        unique_together = ('relatedstudent', 'application', 'key')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(relatedstudent__period__admins=user_obj) | \
                Q(relatedstudent__period__parentnode__admins=user_obj) | \
                Q(relatedstudent__period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def __unicode__(self):
        return '{0}: {1}'.format(self.relatedstudent, super(RelatedStudentKeyValue, self).__unicode__())
