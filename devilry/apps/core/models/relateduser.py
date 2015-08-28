import re

from django.conf import settings
from django.db import models
from django.db.models import Q

from django.core.exceptions import ValidationError

from period import Period
from node import Node
from abstract_is_admin import AbstractIsAdmin
from abstract_applicationkeyvalue import AbstractApplicationKeyValue


class RelatedUserBase(models.Model, AbstractIsAdmin):
    """
    Common fields for examiners and students related to a period.
    """

    #: The period that the user is related to.
    period = models.ForeignKey(Period,
                               verbose_name='Period',
                               help_text="The period.")

    #: A User object. Must be unique within this
    #: period.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, help_text="The related user.")

    #: Comma-separated list of tags. Each tag is a word with the following
    #: letters allowed: a-z and 0-9. Each word is separated by a comma, and no
    #: whitespace.
    #:
    #: .. deprecated:: Since 3.0. Use :class:`.RelatedExaminerSyncSystemTag` and
    #:
    #:    :class:`.RelatedStudentSyncSystemTag` instead.
    #:
    tags = models.TextField(blank=True, null=True,
                            help_text="Comma-separated list of tags. Each tag is a word with the following letters "
                                      "allowed: a-z, 0-9, ``_`` and ``-``. Each word is separated by a comma, "
                                      "and no whitespace.")

    tags_patt = re.compile('^(?:[a-z0-9_-]+,)*[a-z0-9_-]+$')

    class Meta:
        abstract = True
        unique_together = ('period', 'user')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(period__admins=user_obj) | \
               Q(period__parentnode__admins=user_obj) | \
               Q(period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    def clean(self):
        if self.tags and not self.tags_patt.match(self.tags):
            raise ValidationError('tags must be a comma-separated list of tags, each tag only containing '
                                  'a-z, 0-9, ``_`` and ``-``.')

    def __unicode__(self):
        return '{} #{}'.format(self.__class__.__name__, self.id)


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
                                    help_text="If a candidate has the same Candidate ID for all or many assignments "
                                              "in a semester, this field can be set to simplify setting candidate IDs "
                                              "on each assignment.")


class RelatedUserSyncSystemTag(models.Model):
    """
    Base class for :class:`.RelatedExaminerSyncSystemTag` and
    :class:`.RelatedExaminerSyncSystemTag`.
    """

    class Meta:
        abstract = True

    #: A tag unique for a the related student/examiner.
    #: Max 15 characters.
    tag = models.CharField(db_index=True, max_length=15)


class RelatedExaminerSyncSystemTag(RelatedUserSyncSystemTag):
    """
    A tag for a :class:`.RelatedStudent`.

    Used by a third-party sync system to organize students.

    We use this as one of the ways admins can auto-assign examiners
    to students (match :class:`.RelatedExaminerSyncSystemTag` to
    :class:`.RelatedExaminerSyncSystemTag`).
    """

    class Meta:
        unique_together = [
            ('relatedexaminer', 'tag')
        ]

    #: Foreignkey to the :class:`.RelatedExaminer` this tag is for.
    relatedexaminer = models.ForeignKey(RelatedExaminer)


class RelatedStudentSyncSystemTag(RelatedUserSyncSystemTag):
    """
    A tag for a :class:`.RelatedStudent`.

    Used by a third-party sync system to organize tag students.

    We use this as one of the ways admins can auto-assign examiners
    to students (match :class:`.RelatedExaminerSyncSystemTag` to
    :class:`.RelatedExaminerSyncSystemTag`).
    """

    class Meta:
        unique_together = [
            ('relatedstudent', 'tag')
        ]

    #: Foreignkey to the :class:`.RelatedStudent` this tag is for.
    relatedstudent = models.ForeignKey(RelatedStudent)


class RelatedStudentKeyValue(AbstractApplicationKeyValue, AbstractIsAdmin):
    """ Key/value pair tied to a specific RelatedStudent. """
    relatedstudent = models.ForeignKey(RelatedStudent)
    student_can_read = models.BooleanField(
        help_text='Specifies if a student can read the value or not.',
        default=False)

    class Meta:
        unique_together = ('relatedstudent', 'application', 'key')
        app_label = 'core'

    @classmethod
    def q_is_admin(cls, user_obj):
        return (Q(relatedstudent__period__admins=user_obj) |
                Q(relatedstudent__period__parentnode__admins=user_obj) |
                Q(relatedstudent__period__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj)))

    def __unicode__(self):
        return '{0}: {1}'.format(self.relatedstudent, super(RelatedStudentKeyValue, self).__unicode__())
