from datetime import datetime

from django.utils.translation import ugettext as _
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate
from delivery import Delivery

class StaticFeedback(models.Model, AbstractIsExaminer, AbstractIsCandidate):
    """ Represents a feedback for a `Delivery`_.

    Each delivery can have zero or more feedbacks. Each StaticFeedback object stores
    static data that an examiner has published on a delivery. StaticFeedback is
    created and edited in a *grade+feedback editor* in a *grade plugin*, and
    when an examiner chose to publish feedback, a static copy of the data
    he/she created in the *grade+feedback editor* is stored in a StaticFeedback.

    Feedbacks are only visible to students when
    :attr:`Deadline.feedbacks_published` on the related deadline is ``True``.
    Feedbacks are related to Deadlines through its :attr:`delivery`.

    Students are presented with the last feedback on a delivery, however they
    can browse every StaticFeedback on their deliveries. This history is to protect
    the student from administrators or examiners that change published
    feedback to avoid that a student can make an issue out of a bad feedback.

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
    rendered_view = models.TextField()
    grade = models.CharField(max_length=12)
    points = models.PositiveIntegerField(help_text = _('Number of points given on this feedback.'))
    is_passing_grade = models.BooleanField()
    save_timestamp = models.DateTimeField(auto_now=True, blank=False, null=False)
    saved_by = models.ForeignKey(User, blank=False, null=False)


    class Meta:
        app_label = 'core'
        verbose_name = _('Static feedback')
        verbose_name_plural = _('Static feedbacks')
        ordering = ['-save_timestamp']

    @classmethod
    def q_is_candidate(cls, user_obj):
        """
        Returns a django.models.Q object matching Deliveries where
        the given student is candidate.
        """
        return Q(delivery__assignment_group__candidates__student=user_obj)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(delivery__assignment_group__parentnode__publishing_time__lt=now)
        if not active:
            q &= ~Q(deliver__assignment_group__parentnode__parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(delivery__assignment_group__parentnode__parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        """
        Returns a django.models.Q object matching Feedbacks where
        the given student is candidate.
        """
        return Q(delivery__assignment_group__examiners=user_obj)

    def _publish_if_allowed(self):
        assignment = self.delivery.assignment_group.parentnode
        if assignment.examiners_publish_feedbacks_directly:
            deadline = self.delivery.deadline_tag
            deadline.feedbacks_published = True
            deadline.save()

    def save(self, *args, **kwargs):
        super(StaticFeedback, self).save(*args, **kwargs)
        self._publish_if_allowed()

    def __unicode__(self):
        return "StaticFeedback on %s" % self.delivery


def update_deadline_and_assignmentgroup_status(delivery):
    delivery.deadline_tag._update_status()
    delivery.deadline_tag.save()
    delivery.assignment_group._update_status()
    delivery.assignment_group.save()

def feedback_update_assignmentgroup_status_handler(sender, **kwargs):
    feedback = kwargs['instance']
    update_deadline_and_assignmentgroup_status(feedback.delivery)

from django.db.models.signals import post_save
post_save.connect(feedback_update_assignmentgroup_status_handler,
                  sender=StaticFeedback)
