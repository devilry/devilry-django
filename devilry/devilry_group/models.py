# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import warnings
import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import OuterRef
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import ugettext_lazy
from ievv_opensource.utils import choices_with_meta

from devilry.apps.core.models import assignment_group
from devilry.apps.core.models.custom_db_fields import ShortNameField, LongNameField
from devilry.devilry_comment import models as comment_models


class HardDeadlineExpiredException(Exception):
    """
    Should be raised regarding GroupComments
    if the deadline handling is hard, and the deadline has expired.
    """
    def __init__(self, message, *args, **kwargs):
        if not message:
            raise ValueError('Message required. HardDeadlineExpiredException(message="Some message")')
        self.message = message


class PeriodExpiredException(Exception):
    """
    Should be raised regarding GroupComments if the
    period(semester) has expired.
    """
    def __init__(self, message, *args, **kwargs):
        if not message:
            raise ValueError('Message required. PeriodExpiredException(message="Some message")')
        self.message = message


class AbstractGroupCommentQuerySet(models.QuerySet):
    """
    Base class for QuerySets for :class:`.AbstractGroupComment`.
    """
    def exclude_private_comments_from_other_users(self, user):
        """
        Exclude all ``GroupComments`` with :obj:`.GroupComment.visibility` set to :obj:`.GroupComment.VISIBILITY_PRIVATE`
        and the :obj:`.GroupComment.user` is not the ``user``.

        Args:
            user: The requestuser.

        Returns:
            QuerySet: QuerySet of :obj:`.GroupComment` not excluded.
        """
        return self.exclude(
            models.Q(visibility=AbstractGroupComment.VISIBILITY_PRIVATE) & ~models.Q(user=user)
        )

    def exclude_is_part_of_grading_feedbackset_unpublished(self):
        """
        Exclude all :class:`.GroupComment` that has :obj:`.GroupComment.part_of_grading` set to ``True`` if the
        :obj:`.GroupComment.feedback_set.grading_published_datetime` is ``None``.

        Returns:
            QuerySet: QuerySet of :obj:`.GroupComment` not excluded.
        """
        return self.exclude(
            part_of_grading=True,
            feedback_set__grading_published_datetime__isnull=True
        )

    def exclude_comment_is_not_draft_from_user(self, user):
        """
        Exclude :class:`.GroupComment` that are not drafts or the :obj:`.GroupComment.user` is not the requestuser.

        A :class:`.GroupComment` is a draft if :obj:`.GroupComment.visibility` set to
        :obj:`.GroupComment.VISIBILITY_PRIVATE` and :obj:`.GroupComment.part_of_grading` is ``True``.

        Args:
            user: The requestuser

        Returns:
            QuerySet: QuerySet of :obj:`.GroupComment` not excluded.
        """
        return self.exclude(
            ~models.Q(part_of_grading=True, visibility=GroupComment.VISIBILITY_PRIVATE) | ~models.Q(user=user)
        )


class AbstractGroupComment(comment_models.Comment):
    """
    The abstract superclass of all comments related to a delivery and feedback.
    """

    #: The related feedbackset. See :class:`.FeedbackSet`.
    feedback_set = models.ForeignKey('FeedbackSet')

    #: If this is ``True``, the comment is published when the feedbackset
    #: is published. This means that this comment is part of the feedback/grading
    #: from the examiner. The same :obj:`~.AbstractGroupComment.visibility`
    #: rules apply no matter if this is ``True`` or ``False``,
    #: this only controls when the comment is published.
    part_of_grading = models.BooleanField(default=False)

    #: Comment only visible for :obj:`~devilry_comment.models.Comment.user` that created comment.
    #: When this visibility choice is set, and :obj:`~.AbstractGroupComment.part_of_grading` is True, this
    #: GroupComment is a drafted feedback and will be published when the :obj:`~.AbstractGroupComment.feedback_set`
    #  it belongs to is published.
    #: Choice for :obj:`~.AbstractGroupComment.visibility`.
    VISIBILITY_PRIVATE = 'private'

    #: Comment should only be visible to examiners and admins that has
    #: access to the :obj:`~.AbstractGroupComment.feedback_set`.
    #: Choice for :obj:`~.AbstractGroupComment.visibility`.
    VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS = 'visible-to-examiner-and-admins'

    #: Comment should be visible to everyone that has
    #: access to the :obj:`~.AbstractGroupComment.feedback_set`.
    #: Choice for :obj:`~.AbstractGroupComment.visibility`.
    VISIBILITY_VISIBLE_TO_EVERYONE = 'visible-to-everyone'

    #: Choice list.
    #: Choices for :obj:`~.AbstractGroupComment.visibility`.
    VISIBILITY_CHOICES = [
        (VISIBILITY_PRIVATE, 'Private'),
        (VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS, 'Visible to examiners and admins'),
        (VISIBILITY_VISIBLE_TO_EVERYONE, 'Visible to everyone'),
    ]

    #: Sets the visibility choise of the comment.
    #: Defaults to :obj:`~.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`.
    visibility = models.CharField(
        max_length=50,
        db_index=True,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_VISIBLE_TO_EVERYONE,
    )

    class Meta:
        abstract = True

    def clean(self):
        """
        Check for situations that should result in error.

        :raises: ValidationError:
            Error occurs if :obj:`~.AbstractGroupComment.user_role` is ``'student'`` and
            :obj:`~.AbstractGroupComment.visibility` is not set to
            :obj:`~.AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE`
            |
            Error occurs if :obj:`~.AbstractGroupComment.user_role` is ``'examiner'`` and
            :obj:`~.AbstractGroupComment.part_of_grading` is ``False`` and :obj:`~.AbstractGroupComment.visibility` is
            set to :obj:`~.AbstractGroupComment.VISIBILITY_PRIVATE`.
        """
        if self.user_role == 'student':
            if self.visibility != AbstractGroupComment.VISIBILITY_VISIBLE_TO_EVERYONE:
                raise ValidationError({
                    'visibility': ugettext_lazy('A student comment is always visible to everyone'),
                })
        if self.user_role == 'examiner':
            if not self.part_of_grading and self.visibility == AbstractGroupComment.VISIBILITY_PRIVATE:
                raise ValidationError({
                    'visibility': ugettext_lazy('A examiner comment can only be private if part of grading.')
                })

    def get_published_datetime(self):
        """
        Get the publishing datetime of the comment. Publishing datetime is
        the publishing time of the FeedbackSet if the comment has
        :obj:`~devilry.devilry_group.models.AbstractGroupComment.part_of_grading`
        set to True, else it's just the comments' published_datetime.

        :return: Datetime.
        """
        return self.feedback_set.grading_published_datetime \
            if self.part_of_grading \
            else self.published_datetime

    def publish_draft(self, time):
        """
        Sets the published datetime of the comment to ``time``.

        :param time: publishing time to set for the comment.
        """
        self.published_datetime = time
        self.visibility = GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
        self.full_clean()
        self.save()

    def copy_comment_into_feedbackset(self, feedbackset):
        """
        Creates a new GroupComment, copies all fields in self into
        the new comment and sets feedback_set foreign key to ``feedbackset``
        Args:
            feedbackset: :class:`~devilry_group.FeedbackSet`

        Returns:
            :class:`~devilry_group.GroupComment` a new group comment
        """
        commentcopy = GroupComment(
            part_of_grading=self.part_of_grading,
            feedback_set=feedbackset,
            text=self.text,
            draft_text=self.draft_text,
            user=self.user,
            parent=self.parent,
            created_datetime=self.created_datetime,
            published_datetime=self.published_datetime,
            user_role=self.user_role,
            comment_type=self.comment_type,
        )
        commentcopy.save()
        for commentfile in self.commentfile_set.all():
            commentfile.copy_into_comment(commentcopy)
        return commentcopy


class FeedbackSetQuerySet(models.QuerySet):
    """
    QuerySet for :class:`.FeedbackSet`.
    """
    def get_order_by_deadline_datetime_argument(self):
        """
        Get a Coalesce expression that can be used with ``order_by()``
        to order feedbacksets by deadline. This handles
        ordering the first feedbackset by the first deadline of the
        assignment.

        Examples:

            Basics (same as using :meth:`.order_by_deadline_datetime`)::

                FeedbackSet.objects.all()\
                    .order_by(FeedbackSet.objects.get_order_by_deadline_datetime_argument())

            Combine with other order by arguments::

                FeedbackSet.objects.all()\
                    .order_by('group__parentnode__short_name',
                              'group__id',
                              FeedbackSet.objects.get_order_by_deadline_datetime_argument())
        """
        return Coalesce('deadline_datetime', 'group__parentnode__first_deadline')

    def order_by_deadline_datetime(self):
        """
        Order by ``deadline_datetime``.

        Unlike just using ``order_by('deadline_datetime')``, this method
        uses :meth:`.get_order_by_deadline_datetime_argument`, which
        ensures that the first feedbackset is ordered using
        the first deadline of the assignment.
        """
        return self.order_by(self.get_order_by_deadline_datetime_argument())

    def has_public_comment_files_from_students(self, feedback_set):
        """
        Does the FeedbackSet have any public ``CommentFile``s from students?

        Args:
            feedback_set: The ``FeedbackSet`` to check.

        Returns:
            bool: ``True`` if any public student files, else ``False``.
        """
        from devilry.devilry_comment import models as comment_models
        group_comment_ids = GroupComment.objects \
            .filter(feedback_set=feedback_set,
                    user_role=GroupComment.USER_ROLE_STUDENT,
                    visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE) \
            .values_list('id', flat=True)
        return comment_models.CommentFile.objects \
            .filter(id__in=group_comment_ids)\
            .exists()

    def filter_public_comment_files_from_students(self):
        """
        Get all ``FeedbackSet``s with public comments from students.

        Returns:
            QuerySet: A ``FeedbackSet`` queryset.
        """
        from devilry.devilry_comment import models as comment_models
        comment_file_ids = comment_models.CommentFile.objects.all()\
            .values_list('comment_id')
        feedback_set_ids = GroupComment.objects \
            .filter(user_role=GroupComment.USER_ROLE_STUDENT,
                    visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE) \
            .filter(id__in=comment_file_ids) \
            .values_list('feedback_set_id', flat=True)
        return FeedbackSet.objects.filter(id__in=feedback_set_ids)


class FeedbackSet(models.Model):
    """
    All comments that are given for a specific deadline (delivery and feedback) are
    linked to a feedback-set.

    If the comment has `instant_publish=True` it will be published instantly, otherwise the comments will only be
    visible once the feedbackset is published.
    All student-comments will be `instant_publish=True`, and the same applies to comments made by examiners that
    are not a part of feedback.
    """
    objects = FeedbackSetQuerySet.as_manager()

    #: The AssignmentGroup that owns this feedbackset.
    group = models.ForeignKey(assignment_group.AssignmentGroup)

    #: This means the feedbackset is basically the first feedbackset.
    #: Choice for :obj:`~.FeedbackSet.feedbackset_type`.
    FEEDBACKSET_TYPE_FIRST_ATTEMPT = 'first_attempt'

    #: Is not the first feedbackset, but a new attempt.
    #: Choice for :obj:`~.FeedbackSet.feedbackset_type`
    FEEDBACKSET_TYPE_NEW_ATTEMPT = 'new_attempt'

    #: Something went wrong on grading, with this option, a new
    #: deadline should not be given to student. Student should just
    #: get notified that a new feedback was given.
    #: Choice for :obj:`~.FeedbackSet.feedbackset_type`.
    FEEDBACKSET_TYPE_RE_EDIT = 're_edit'

    #: A merged first attempt feedbackset
    FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT = 'merge_first_attempt'

    #: A merged new attempt feedbackset
    FEEDBACKSET_TYPE_MERGE_NEW_ATTEMPT = 'merge_new_attempt'

    #: A merged re edit feedbackset
    FEEDBACKSET_TYPE_MERGE_RE_EDIT = 'merge_re_edit'

    #: Grading status choices for :obj:`~.FeedbackSet.feedbackset_type`.
    FEEDBACKSET_TYPE_CHOICES = [
        (FEEDBACKSET_TYPE_FIRST_ATTEMPT, ugettext_lazy('first attempt')),
        (FEEDBACKSET_TYPE_NEW_ATTEMPT, ugettext_lazy('new attempt')),
        (FEEDBACKSET_TYPE_RE_EDIT, ugettext_lazy('re edit')),
        (FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT, ugettext_lazy('merge first attempt')),
        (FEEDBACKSET_TYPE_MERGE_NEW_ATTEMPT, ugettext_lazy('merge new attempt')),
        (FEEDBACKSET_TYPE_MERGE_RE_EDIT, ugettext_lazy('merge re edit')),
    ]

    #: Sets the type of the feedbackset.
    #: Defaults to :obj:`~.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT`.
    feedbackset_type = models.CharField(
        max_length=50,
        db_index=True,
        choices=FEEDBACKSET_TYPE_CHOICES,
        default=FEEDBACKSET_TYPE_NEW_ATTEMPT
    )

    #: Field can be set to ``True`` if a situation requires the :obj:`~.FeedbackSet` to not be counted as neither
    #: passed or failed but should be ignored, due to e.g sickness or something else. A reason for
    #: the :obj:`~.FeedbackSet` to be ignored must be provided in the :attr:`~FeedbackSet.ignored_reason`.
    ignored = models.BooleanField(default=False)

    #: The reason for the :obj:`~FeedbackSet` to be ignored.
    ignored_reason = models.TextField(null=False, blank=True, default='')

    #: The datetime for when the :obj:`~.FeedbackSet` was ignored.
    ignored_datetime = models.DateTimeField(null=True, blank=True)

    #: The User that created the feedbackset. Only used as metadata
    #: for superusers (for debugging).
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_feedbacksets",
        null=True, blank=True,
        on_delete=models.SET_NULL)

    #: The datetime when this FeedbackSet was created.
    created_datetime = models.DateTimeField(default=timezone.now)

    #: Last updated by.
    #: The user that was the last to make any changes on the :obj:`.FeedbackSet`.
    last_updated_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='updated_feedbacksets'
    )

    #: The datetime of the deadline.
    #: The first feedbackset in an AssignmentGroup
    #: (ordered by :obj:`~.FeedbackSet.created_datetime`) does not
    #: have a deadline. It inherits this from the ``first_deadline`` field
    #: of :class:`devilry.apps.core.models.assignment.Assignment`.
    deadline_datetime = models.DateTimeField(null=False, blank=False)

    #: The datetime when the feedback was published.
    #: Set when an examiner publishes the feedback for this FeedbackSet.
    #:
    #: When this is ``None``, the feedbackset is not published. This means that
    #: no comments with :obj:`.AbstractGroupComment.part_of_grading` set to ``True``
    #: is visible, the grade (extracted from points) is not visible, and this
    #: feedbackset does not count when extracting the latest/active feedback/grade
    #: for the AssignmentGroup.
    grading_published_datetime = models.DateTimeField(
        null=True,
        blank=True
    )

    #: Set when the feedbackset is published by an examiner.
    #: If this is ``None``, the feedback is not published, and
    #: the ``points`` (grade) is not available to the student.
    grading_published_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        related_name="published_feedbacksets",
        null=True, blank=True,
        on_delete=models.SET_NULL
    )

    #: Points given by examiner for this feedbackset.
    #: The points on the last published FeedbackSet is the current
    #: grade for the AssignmentGroup.
    grading_points = models.PositiveIntegerField(
        null=True, blank=True
    )

    #: A :class:`django.db.models.TextField` for a gradeform filled or not filled for
    #: FeedbackSet.
    gradeform_data_json = models.TextField(
        null=False, blank=True, default=''
    )

    def __unicode__(self):
        return u"{} - {} - {} - deadline: {} - points: {}".format(
                self.group.assignment,
                self.feedbackset_type,
                self.group.get_unanonymized_long_displayname(),
                self.current_deadline(),
                self.grading_points)

    @classmethod
    def clean_deadline(cls, deadline_datetime):
        return deadline_datetime.replace(microsecond=0)
    
    @property
    def is_merge_type(self):
        return self.feedbackset_type == self.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT or \
               self.feedbackset_type == self.FEEDBACKSET_TYPE_MERGE_NEW_ATTEMPT or \
               self.feedbackset_type == self.FEEDBACKSET_TYPE_MERGE_RE_EDIT
    
    def clean(self):
        """
        Check for situations that should result in error.

        :raises: ValidationError:
            Error occurs if :attr:`~.FeedbackSet.ignored` is ``True`` and :obj:`~.FeedbackSet.ignored_reason` is blank.
            |
            Error occurs if :attr:`~.FeedbackSet.ignored_reason` is filled and :attr:`~.FeedbackSet.ignored`
            is ``True``.
            |
            Error occurs if :attr:`~.FeedbackSet.grading_published_datetime` has a datetime but
            :obj:`~.FeedbackSet.grading_published_by` is ``None``.
            |
            Error occurs if :attr:`~.FeedbackSet.grading_published_datetime` has a datetime but
            :obj:`~.FeedbackSet.grading_points` is ``None``.
        """
        if self.ignored and len(self.ignored_reason) == 0:
            raise ValidationError({
                'ignored': ugettext_lazy('FeedbackSet can not be ignored without a reason')
            })
        elif len(self.ignored_reason) > 0 and not self.ignored:
            raise ValidationError({
                'ignored_reason': ugettext_lazy('FeedbackSet can not have a ignored reason '
                                                'without being set to ignored.')
            })
        elif self.ignored and (self.grading_published_datetime or self.grading_points or self.grading_published_by):
            raise ValidationError({
                'ignored': ugettext_lazy('Ignored FeedbackSet can not have grading_published_datetime, '
                                         'grading_points or grading_published_by set.')
            })
        else:
            if self.grading_published_datetime is not None and self.grading_published_by is None:
                raise ValidationError({
                    'grading_published_datetime': ugettext_lazy('A FeedbackSet can not be published '
                                                                'without being published by someone.'),
                })
            if self.grading_published_datetime is not None and self.grading_points is None:
                raise ValidationError({
                    'grading_published_datetime': ugettext_lazy('A FeedbackSet can not be published '
                                                                'without providing "points".'),
                })
        self.deadline_datetime = FeedbackSet.clean_deadline(self.deadline_datetime)

    def current_deadline(self, assignment=None):
        warnings.warn("deprecated, use FeedbackSet.deadline_datetime instead", DeprecationWarning)
        return self.deadline_datetime

    def __get_drafted_comments(self, user):
        """
        Get all drafted comments for this FeedbackSet drafted by ``user``.

        :param user: Current user.
        :return: QuerySet of GroupComments
        """
        return GroupComment.objects.filter(
            feedback_set=self,
            part_of_grading=True
        ).exclude_private_comments_from_other_users(
            user=user
        ).order_by('created_datetime')

    def can_add_comment(self, comment_user_role, assignment=None):
        """
        Check if comments and uploads should be disabled for this feedback set
        for the role of the comment.

        This method raises a custom exception based on what why comments and uploads are not allowed:

        Raises :class:`~.HardDeadlineExpiredException` if the assignment for this feedback set has deadline
        handling set to hard, students can not upload or add comments.

        Raises :class:`~.PeriodExpiredException` if the period has expired, no one can upload or
        add comments.

        A message will be provided with the exceptions.

        Args:
            comment_user_role: One of the choices for :class:`~devilry.devilry_comment.models.Comment.user_role`.
                ``Comment.USER_ROLE_STUDENT``, ``Comment.USER_ROLE_EXAMINER`` or ``Comment.USER_ROLE_ADMIN``.
            assignment: The assignment for this feedback set.
        """
        if not assignment:
            assignment = self.group.assignment
        period = assignment.period
        now = timezone.now()
        if period.start_time > now or period.end_time < now:
            raise PeriodExpiredException(
                message=ugettext_lazy('This assignment is on an inactive semester. '
                                      'File upload and commenting is disabled.')
            )
        if assignment.deadline_handling_is_hard() and self.deadline_datetime < now:
            if comment_user_role == comment_models.Comment.USER_ROLE_STUDENT:
                raise HardDeadlineExpiredException(
                    message=ugettext_lazy('Hard deadlines are enabled for this assignment. '
                                          'File upload and commenting is disabled.')
                )

    def publish(self, published_by, grading_points, gradeform_data_json=''):
        """
        Publishes this FeedbackSet and comments that belongs to this it and that are
        part of the grading.

        :param published_by: Who published the feedbackset.
        :param grading_points: Points to give to student(s).
        :param gradeform_data_json: gradeform(coming soon).
        :return: True or False and an error message.
        """
        current_deadline = self.deadline_datetime
        if current_deadline is None:
            return False, 'Cannot publish feedback without a deadline.'

        drafted_comments = self.__get_drafted_comments(published_by)
        now_without_seconds = timezone.now().replace(microsecond=0)
        for modifier, draft in enumerate(drafted_comments):
            draft.publish_draft(now_without_seconds + timezone.timedelta(microseconds=modifier))

        self.grading_points = grading_points
        self.grading_published_datetime = now_without_seconds + timezone.timedelta(
            microseconds=drafted_comments.count() + 1)
        self.grading_published_by = published_by
        self.full_clean()
        self.save()

        return True, ''

    def copy_feedbackset_into_group(self, group, target=None):
        """
        Copy this feedbackset into ``target`` or create a new feedbackset,
        and set group foreign key to ``group``

        Args:
            group: :class:`~core.AssignmentGroup`
            target: :class:`~devilry_group.FeedbackSet`

        Returns:
            :class:`~devilry_group.FeedbackSet` a feedbackset with copied data from self

        """
        feedbackset_kwargs = {
            'group': group,
            'feedbackset_type': self.feedbackset_type,
            'ignored': self.ignored,
            'ignored_reason': self.ignored_reason,
            'ignored_datetime': self.ignored_datetime,
            'created_by': self.created_by,
            'created_datetime': self.created_datetime,
            'deadline_datetime': self.deadline_datetime,
            'grading_published_datetime': self.grading_published_datetime,
            'grading_published_by': self.grading_published_by,
            'grading_points': self.grading_points,
            'gradeform_data_json': self.gradeform_data_json
        }
        if target is None:
            target = FeedbackSet(**feedbackset_kwargs)
        else:
            for key, value in feedbackset_kwargs.iteritems():
                setattr(target, key, value)
        target.save()

        for comment in self.groupcomment_set.all():
            comment.copy_comment_into_feedbackset(target)

        return target

    @property
    def gradeform_data(self):
        if self.gradeform_data_json:
            if not hasattr(self, '_gradeform_data'):
                # Store the decoded gradeform_data to avoid re-decoding the json for
                # each access. We invalidate this cache in the setter.
                self._gradeform_data = json.loads(self.gradeform_data_json)
            return self._gradeform_data
        else:
            return None

    @gradeform_data.setter
    def gradeform_data(self, gradeform_data):
        self.gradeform_data_json = json.dumps(gradeform_data)
        if hasattr(self, '_gradeform_data'):
            delattr(self, '_gradeform_data')


class FeedbacksetPassedPreviousPeriod(models.Model):
    """
    This model is used when a student have passed an assignment in previous period.
    Therefore we need to save some old data about the :class:`core.Assignment`, :class:`devilry_group.FeedbackSet`
    and :class:`core.Period` from previous period.
    """
    PASSED_PREVIOUS_SEMESTER_TYPES = choices_with_meta.ChoicesWithMeta(
        choices_with_meta.Choice(
            value='manual'
        ),
        choices_with_meta.Choice(
            value='auto'
        )
    )

    #: Foreign key to class:`devilry_group.FeedbackSet` in current period.
    feedbackset = models.OneToOneField(
        to=FeedbackSet,
        null=True, blank=True,
        on_delete=models.CASCADE)

    #: The type of this entry. How it was generated.
    passed_previous_period_type = models.CharField(
        max_length=255,
        null=False, blank=False,
        choices=PASSED_PREVIOUS_SEMESTER_TYPES.iter_as_django_choices_short()
    )

    #: Old :attr:`core.Assignment.short_name`.
    assignment_short_name = ShortNameField(
        blank=True, default=''
    )

    #: Old :attr:`core.Assignment.long_name`.
    assignment_long_name = LongNameField(
        blank=True, default=''
    )

    # Old :attr:`core.Assignment.max_points`.
    assignment_max_points = models.PositiveIntegerField(
        default=0, null=True, blank=True
    )

    # Old :attr:`core.Assignment.passing_grade_min_points`
    assignment_passing_grade_min_points = models.PositiveIntegerField(
        default=0, null=True, blank=True
    )

    # Old :attr:`core.Period.short_name`.
    period_short_name = ShortNameField(
        blank=True, default=''
    )

    # Old :attr:`core.Period.long_name`
    period_long_name = LongNameField(
        blank=True, default=''
    )

    # Old :attr:`core.Period.start_time`
    period_start_time = models.DateTimeField(
        null=True, default=None
    )

    # Old :attr:`core.Period.end_time`
    period_end_time = models.DateTimeField(
        null=True, default=None
    )

    # Old :attr:`FeedbackSet.grading_points`.
    grading_points = models.PositiveIntegerField(
        default=0, null=True, blank=True
    )

    # Old :attr:`FeedbackSet.grading_published_by`
    grading_published_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='passed_previous_period_published_by'
    )

    # Old :attr:`FeedbackSet.
    grading_published_datetime = models.DateTimeField(
        null=True, default=None
    )

    #: When this entry was created.
    created_datetime = models.DateTimeField(
        default=timezone.now
    )

    #: Who this entry was created by.
    created_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='passed_previous_period_created_by'
    )


class FeedbackSetGradingUpdateHistory(models.Model):
    """
    Logs changes on the grading for a feedbackset.

    If we have this history, there will be no problem changing the grades on an already corrected feedback set, as we
    can display the history, just as with FeedbackSetDeadlineHistory.
    """
    #: The :class:`~.FeedbackSet` the update is for.
    feedback_set = models.ForeignKey(
        to=FeedbackSet,
        on_delete=models.CASCADE,
        related_name='grading_update_histories'
    )

    #: The user that updated the feedback set.
    updated_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    #: When the update was made.
    updated_datetime = models.DateTimeField(
        default=timezone.now
    )

    #: The score before update
    old_grading_points = models.PositiveIntegerField(
        null=False, blank=False
    )

    #: Who published the feedbackset before the update.
    old_grading_published_by = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    #: Grading publishing datetime before update
    old_grading_published_datetime = models.DateTimeField(
        null=False, blank=False
    )

    def __str__(self):
        return 'FeedbackSet id: {} - points: {} - updated_datetime: {}'.format(
            self.feedback_set.id, self.old_grading_points, self.updated_datetime)


class FeedbackSetDeadlineHistory(models.Model):
    """
    Logs change in deadline for a FeedbackSet.
    """
    #: The :class:`~.FeedbackSet` the change is for.
    feedback_set = models.ForeignKey(FeedbackSet)

    #: The User that made the deadline change.
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    #: Time of change.
    #: Defaults to ``timezone.now``.
    changed_datetime = models.DateTimeField(null=False, blank=False, default=timezone.now)

    #: The old :attr:`~.FeedbackDet.deadline_datetime`.
    deadline_old = models.DateTimeField(null=False, blank=False)

    #: The new :attr:`~.FeedbackDet.deadline_datetime`.
    deadline_new = models.DateTimeField(null=False, blank=False)

    def __unicode__(self):
        return u'Changed {}: from {} to {}'.format(self.changed_datetime, self.deadline_old, self.deadline_new)


class GroupCommentQuerySet(AbstractGroupCommentQuerySet):
    """
    QuerySet for :class:`.GroupComment`.
    """
    def annotate_with_last_edit_history(self, requestuser_devilryrole):
        edit_history_subquery = GroupCommentEditHistory.objects \
            .filter(group_comment_id=OuterRef('id'))

        if requestuser_devilryrole == 'student':
            edit_history_subquery = edit_history_subquery\
                .filter(visibility=GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE)

        edit_history_subquery = edit_history_subquery\
            .order_by('-edited_datetime')\
            .values('edited_datetime')[:1]
        return self.annotate(
            last_edithistory_datetime=models.Subquery(
                edit_history_subquery, output_field=models.DateTimeField()
            )
        )


class GroupComment(AbstractGroupComment):
    """
    A comment made to an `AssignmentGroup`.
    """
    objects = GroupCommentQuerySet.as_manager()

    #: v2 "<modelname>_<id>"
    #: This is only here to make it possible to debug and fix
    #: v2 migrations if anything goes wrong.
    v2_id = models.CharField(
        max_length=255,
        null=False, blank=True, default="")

    def __unicode__(self):
        return u"{} - {} - {}".format(self.feedback_set, self.user_role, self.user)

    def clean(self):
        try:
            self.feedback_set.can_add_comment(
                comment_user_role=self.user_role,
                assignment=self.feedback_set.group.parentnode)
        except (HardDeadlineExpiredException, PeriodExpiredException) as e:
            raise ValidationError(message=e.message)
        super(GroupComment, self).clean()


class GroupCommentEditHistoryQuerySet(models.QuerySet):
    def exclude_private_comment_not_created_by_user(self, user):
        """
        Exclude all :class:`.GroupCommentEditHistory` entries that are private and
        where the comment is not created by the user.

        Args:
            user: The user to check against.
        """
        return self.exclude(
            models.Q(visibility=GroupComment.VISIBILITY_PRIVATE)
            &
            ~models.Q(group_comment__user=user))


class GroupCommentEditHistory(comment_models.CommentEditHistory):
    """
    Model for logging changes in a :class:`.GroupComment`.
    """
    objects = GroupCommentEditHistoryQuerySet.as_manager()

    #: The :class:`.GroupComment` the editing history is for.
    group_comment = models.ForeignKey(
        to=GroupComment,
        on_delete=models.CASCADE
    )

    #: Visibility state when log entry was created.
    visibility = models.CharField(
        max_length=50,
        db_index=True
    )

    def __unicode__(self):
        return 'GroupComment: {} - {}'.format(self.group_comment.user_role, self.group_comment.user)


class ImageAnnotationCommentQuerySet(AbstractGroupCommentQuerySet):
    """
    QuerySet for :class:`.ImageAnnotationComment`.
    """


class ImageAnnotationComment(AbstractGroupComment):
    """
    A comment made on a file, as an annotation
    """
    objects = ImageAnnotationCommentQuerySet.as_manager()

    image = models.ForeignKey(comment_models.CommentFileImage)
    x_coordinate = models.PositiveIntegerField()
    y_coordinate = models.PositiveIntegerField()
