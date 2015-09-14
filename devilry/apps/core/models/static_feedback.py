from datetime import datetime
import os
import uuid
from django.conf import settings
from django.core.urlresolvers import reverse

from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError

from abstract_is_admin import AbstractIsAdmin
from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate
from delivery import Delivery
from devilry.devilry_account.models import User
from node import Node


class StaticFeedback(models.Model, AbstractIsAdmin, AbstractIsExaminer, AbstractIsCandidate):
    """ Represents a feedback for a `Delivery`_.

    Each delivery can have zero or more feedbacks. Each StaticFeedback object stores
    static data that an examiner has published on a delivery. StaticFeedback is
    created and edited in a *grade+feedback editor* in a *grade plugin*, and
    when an examiner choose to publish feedback, a static copy of the data
    he/she created in the *grade+feedback editor* is stored in a StaticFeedback.

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

       The User that created the StaticFeedback.

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
    is_passing_grade = models.BooleanField(
        help_text='Is this a passing grade?',
        default=False)
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
        return \
            Q(delivery__deadline__assignment_group__parentnode__admins=user_obj) | \
            Q(delivery__deadline__assignment_group__parentnode__parentnode__admins=user_obj) | \
            Q(delivery__deadline__assignment_group__parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(delivery__deadline__assignment_group__parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(  # noqa
                user_obj))

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
        q = Q(delivery__deadline__assignment_group__parentnode__publishing_time__lt=now)
        if not active:
            q &= ~Q(delivery__deadline__assignment_group__parentnode__parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(delivery__deadline__assignment_group__parentnode__parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        """
        Returns a django.models.Q object matching Feedbacks where
        the given student is candidate.
        """
        return Q(delivery__deadline__assignment_group__examiners__user=user_obj)

    @classmethod
    def from_points(cls, points, assignment=None, **kwargs):
        """
        Shortcut method to initialize the StaticFeedback object
        from points.

        Initializes a StaticFeedback with the given points, with grade
        and is_passing_grade inferred from the points with the help
        of :meth:`devilry.apps.core.models.Assignment.points_to_grade`
        and :meth:`devilry.apps.core.models.Assignment.points_is_passing_grade`.

        Examples:
            ::

                feedback = StaticFeedback.from_points(
                    assignment=myassignment,
                    points=10,
                    delivery=mydelivery,
                    saved_by=someuser)
                assert(feedback.id == None)
                assert(feedback.grade != None)

        :param points:
            The number of points for the feedback.
        :param assignment:
            An Assignment object. Should be the assignment where delivery
            this feedback is for belongs, but that is not checked.

            Defaults to ``self.delivery.deadline.assignment_group.assignment``.

            We provide the ability to take the assignment as argument instead
            of looking it up via ``self.delivery.deadline.assignment_group``
            because we want to to be efficient when creating feedback in bulk.

        :param kwargs:
            Extra kwargs for the StaticFeedback constructor.
        :return: An (unsaved) StaticFeedback.
        """
        if not assignment:
            assignment = kwargs['delivery'].assignment
        is_passing_grade = assignment.points_is_passing_grade(points)
        grade = assignment.points_to_grade(points)
        feedback = cls(
            points=points,
            is_passing_grade=is_passing_grade,
            grade=grade, **kwargs
        )
        feedback.clean(assignment=assignment)
        return feedback

    def _close_group(self):
        self.delivery.deadline.assignment_group.is_open = False
        self.delivery.deadline.assignment_group.save()

    def save(self, *args, **kwargs):
        """
        :param autoset_timestamp_to_now:
            Automatically set the ``timestamp``-attribute of this model
            to *now*? Defaults to ``True``.
        :param autoupdate_related_models:
            Automatically update related models:

            - Sets the ``last_feedback``-attribute of ``self.delivery`` and saved the delivery.
            - Sets the ``feedback`` and ``is_open`` attributes of
              ``self.delivery.deadline.assignment_group`` to this feedback, and ``False``.
              Saves the AssignmentGroup.

            Defaults to ``True``.
        """
        autoupdate_related_models = kwargs.pop('autoupdate_related_models', True)
        autoset_timestamp_to_now = kwargs.pop('autoset_timestamp_to_now', True)
        if autoset_timestamp_to_now:
            self.save_timestamp = datetime.now()
        super(StaticFeedback, self).save(*args, **kwargs)
        if autoupdate_related_models:
            delivery = self.delivery
            self.delivery.last_feedback = self
            self.delivery.save()

            group = delivery.deadline.assignment_group
            group.feedback = self
            group.is_open = False
            group.save()

    def clean(self, assignment=None):
        if not assignment:  # See from_points() for why we do this
            assignment = self.delivery.assignment
        max_points = assignment.max_points
        if self.points > max_points:
            raise ValidationError(
                _('You are not allowed to give more than {max_points} points on this assignment.').format(
                    max_points=max_points))

    def __unicode__(self):
        return "StaticFeedback on %s" % self.delivery

    def copy(self, newdelivery):
        """
        Copy this StaticFeedback into ``newdeadline``.

        .. note::
            This only copies the StaticFeedback, not any data related to it
            via any grade editors.

        .. warning::
            This does not autoset the feedback as active on the group or as latest on the delivery.
            You need to handle that yourself after the copy.
        """
        feedbackcopy = StaticFeedback(delivery=newdelivery,
                                      rendered_view=self.rendered_view,
                                      grade=self.grade,
                                      points=self.points,
                                      is_passing_grade=self.is_passing_grade,
                                      save_timestamp=self.save_timestamp,
                                      saved_by=self.saved_by)
        feedbackcopy.full_clean()
        feedbackcopy.save(autoupdate_related_models=False,
                          autoset_timestamp_to_now=False)
        return feedbackcopy


def staticfeedback_fileattachment_upload_to(instance, filename):
    extension = os.path.splitext(filename)[1]
    return u'devilry_core/staticfeedbackfileattachment/{staticfeedback_id}/{uuid}{extension}'.format(
        staticfeedback_id=instance.staticfeedback_id,
        uuid=str(uuid.uuid1()),
        extension=extension)


class StaticFeedbackFileAttachment(models.Model):
    """
    A file attachment for a :class:`.StaticFeedback`.
    """

    #: The :class:`.StaticFeedback` where that the file is attached to.
    staticfeedback = models.ForeignKey(StaticFeedback, related_name='files')

    #: The original filename.
    filename = models.TextField(blank=False, null=False)

    #: The uploaded file.
    file = models.FileField(
        upload_to=staticfeedback_fileattachment_upload_to
    )

    class Meta:
        app_label = 'core'
        verbose_name = 'Static feedback file attachment'
        verbose_name_plural = 'Static feedback file attachments'
        ordering = ['filename']

    def get_download_url(self):
        """
        Get the URL where anyone with access to the file can download it.
        """
        return reverse('devilry_core_feedbackfileattachment', kwargs={
            'pk': self.pk,
            'asciifilename': self.get_ascii_filename()
        })

    def get_ascii_filename(self):
        return self.filename.encode('ascii', 'ignore')

    def __unicode__(self):
        return u'StaticFeedbackFileAttachment#{} StaticFeedback#{}'.format(
            self.pk, self.staticfeedback_id)
