from datetime import datetime

from django.utils.translation import ugettext as _
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from abstract_is_admin import AbstractIsAdmin
from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate
from delivery import Delivery
from node import Node

class StaticFeedback(models.Model, AbstractIsAdmin, AbstractIsExaminer, AbstractIsCandidate):
    """ Represents a feedback for a `Delivery`_.

    Each delivery can have zero or more feedbacks. Each StaticFeedback object stores
    static data that an examiner has published on a delivery. StaticFeedback is
    created and edited in a *grade+feedback editor* in a *grade plugin*, and
    when an examiner choose to publish feedback, a static copy of the data
    he/she created in the *grade+feedback editor* is stored in a StaticFeedback.

    Feedbacks are only visible to students when
    :attr:`Deadline.feedbacks_published` on the related deadline is ``True``.
    Feedbacks are related to Deadlines through its :attr:`delivery`.

    Students are presented with the last feedback on a delivery, however they
    can browse every StaticFeedback on their deliveries. This history is to protect
    the student from administrators or examiners that change published
    feedback to avoid that a student can make an issue out of a bad feedback.

    **NOTE:** When a StaticFeedback is saved, the corresponding
    :attr:`AssignmentGroup.feedback` is updated to the newly created
    StaticFeedback.

    .. attribute:: rendered_view

        The rendered HTML view.

    .. attribute:: saved_by

       The django.contrib.auth.models.User_ that created the StaticFeedback.

    .. attribute:: save_timestamp

       Date/time when this feedback was created.

    .. attribute:: delivery

       A django.db.models.ForeignKey_ that points to the `Delivery`_ where this feedback belongs.

    .. attribute:: grade

        The grade as a short string (max 12 chars).

    .. attribute:: points

        The number of points (integer).

    .. attribute:: is_passing_grade

        Boolean is passing grade?

    """
    delivery = models.ForeignKey(Delivery, related_name='feedbacks')
    rendered_view = models.TextField(blank=True,
                                     help_text=('A rendered HTML version of the feedback, containing '
                                                 'whatever the grade-editor chose to dump in this field.'))
    grade = models.CharField(max_length=12, help_text='The rendered grade, such as "A" or "approved".')
    points = models.PositiveIntegerField(help_text='Number of points given on this feedback.')
    is_passing_grade = models.BooleanField(help_text='Is this a passing grade?')
    save_timestamp = models.DateTimeField(blank=True, null=True,
                                          help_text=('Time when this feedback was saved. Since StaticFeedback '
                                                     'is immutable, this never changes.'))
    saved_by = models.ForeignKey(User, blank=False, null=False,
                                 help_text='The user (examiner) who saved this feedback')
    class Meta:
        app_label = 'core'
        verbose_name = 'Static feedback'
        verbose_name_plural = 'Static feedbacks'
        ordering = ['-save_timestamp']

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(delivery__deadline__assignment_group__parentnode__admins=user_obj) | \
                Q(delivery__deadline__assignment_group__parentnode__parentnode__admins=user_obj) | \
                Q(delivery__deadline__assignment_group__parentnode__parentnode__parentnode__admins=user_obj) | \
                Q(delivery__deadline__assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def q_is_candidate(cls, user_obj):
        """
        Returns a django.models.Q object matching Deliveries where
        the given student is candidate.
        """
        return Q(delivery__deadline__assignment_group__candidates__student=user_obj)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(delivery__deadline__assignment_group__parentnode__publishing_time__lt = now)
        if not active:
            q &= ~Q(delivery__deadline__assignment_group__parentnode__parentnode__end_time__gte = now)
        if not old:
            q &= ~Q(delivery__deadline__assignment_group__parentnode__parentnode__end_time__lt = now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        """
        Returns a django.models.Q object matching Feedbacks where
        the given student is candidate.
        """
        return Q(delivery__deadline__assignment_group__examiners__user=user_obj)

    def _publish_if_allowed(self):
        assignment = self.delivery.deadline.assignment_group.parentnode
        if assignment.examiners_publish_feedbacks_directly:
            deadline = self.delivery.deadline
            deadline.feedbacks_published = True
            deadline.save()

    def _set_as_active_feedback_on_group(self):
        group = self.delivery.deadline.assignment_group
        group.feedback = self
        group.save()

    def _close_group(self):
        self.delivery.deadline.assignment_group.is_open = False
        self.delivery.deadline.assignment_group.save()

    def save(self, *args, **kwargs):
        autoclose_group = kwargs.pop('autoclose_group', True)
        autoset_as_active_feedback_on_group = kwargs.pop('autoset_as_active_feedback_on_group', True)
        autoset_timestamp_to_now = kwargs.pop('autoset_timestamp_to_now', True)
        if autoset_timestamp_to_now:
            self.save_timestamp = datetime.now()
        super(StaticFeedback, self).save(*args, **kwargs)
        if autoclose_group:
            self._close_group()
        if autoset_as_active_feedback_on_group:
            self._set_as_active_feedback_on_group()
        self._publish_if_allowed()

    def __unicode__(self):
        return "StaticFeedback on %s" % self.delivery

    def copy(self, newdelivery):
        """
        Copy this StaticFeedback into ``newdeadline``.

        .. note::
            This only copies the StaticFeedback, not any data related to it
            via any grade editors.

        .. warning::
            This does not autoset the feedback as active on the group. You
            need to handle that yourself after the copy.
        """
        feedbackcopy = StaticFeedback(delivery=newdelivery,
                                      rendered_view=self.rendered_view,
                                      grade=self.grade,
                                      points=self.points,
                                      is_passing_grade=self.is_passing_grade,
                                      save_timestamp=self.save_timestamp,
                                      saved_by=self.saved_by)
        feedbackcopy.full_clean()
        feedbackcopy.save(autoclose_group=False,
                          autoset_as_active_feedback_on_group=False,
                          autoset_timestamp_to_now=False)
        return feedbackcopy
