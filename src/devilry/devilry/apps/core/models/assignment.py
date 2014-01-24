from datetime import datetime

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.conf import settings

from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from basenode import BaseNode
from node import Node
from period import Period
from abstract_is_examiner import AbstractIsExaminer
from abstract_is_candidate import AbstractIsCandidate
from candidate import Candidate
from model_utils import *
from custom_db_fields import ShortNameField, LongNameField
from model_utils import Etag

import deliverytypes


class AssignmentQuerySet(models.query.QuerySet):
    def filter_is_examiner(self, user):
        """
        Returns a queryset with all Assignments  where the given ``user`` is examiner.

        WARNING: You should normally not use this directly because it gives the
        examiner information from expired periods (which in most cases are not necessary
        to get). Use :meth:`.filter_examiner_has_access` instead.
        """
        return self.filter(assignmentgroups__examiners__user=user).distinct()

    def filter_is_active(self):
        """
        Returns all active assignments (published assignments within a period that is currently started and not ended).
        """
        now = datetime.now()
        return self.filter(
            publishing_time__lt=now,
            parentnode__start_time__lt=now,
            parentnode__end_time__gt=now)

    def filter_examiner_has_access(self, user):
        """
        Returns all assignments that the given ``user`` has access to as examiner.
        """
        return self.filter_is_active().filter_is_examiner(user)

    def filter_admin_has_access(self, user):
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(Assignment.q_is_admin(user)).distinct()


class AssignmentManager(models.Manager):
    """
    Reflect custom QuerySet methods for custom QuerySet
    more info: https://github.com/devilry/devilry-django/issues/491
    """

    def get_queryset(self):
        return AssignmentQuerySet(self.model, using=self._db)

    def filter_is_examiner(self, user):
        return self.get_queryset().filter_is_examiner(user)

    def filter_is_active(self):
        return self.get_queryset().filter_is_active()

    def filter_examiner_has_access(self, user):
        """
        Returns a queryset with all active assignments where the given ``user`` is examiner.

        NOTE: This returns all assignments that the given ``user`` has examiner-rights for.
        """
        return self.get_queryset().filter_examiner_has_access(user)

    def filter_admin_has_access(self, user):
        """
        Returns a queryset with all active assignments where the given
        ``user`` is admin, including assignment where the user is admin higher
        up in the hierarchy.

        NOTE: This returns all assignments that the given ``user`` has admin-rights for.
        """
        return self.get_queryset().filter_admin_has_access(user)




class Assignment(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate, Etag):
    """

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Period`_.

    .. attribute:: publishing_time

        A django.db.models.DateTimeField_ representing the publishing time of
        the assignment.

    .. attribute:: anonymous

        A models.BooleanField specifying if the assignment should be
        anonymously for correcters.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        Node.

    .. attribute:: assignmentgroups

        A set of :class:`assignmentgroups <devilry.apps.core.models.AssignmentGroup>` for this assignment

    .. attribute:: examiners_publish_feedbacks_directly

       Should feedbacks published by examiners be made avalable to the
       students immediately? If not, an administrator have to publish
       feedbacks. See also :attr:`Deadline.feedbacks_published`.

    .. attribute:: scale_points_percent

        Percent to scale points on this assignment by for period overviews. The default is 100, which means no change to the points.

    .. attribute:: delivery_types

        An integer identifying the type of deliveries allowed. Possible values:

            0
                Electronic deliveries using Devilry
            1
                Non-electronic deliveries, or deliveries made through another
                electronic system.
            2
                An alias/link to a delivery made in another Period.

    .. attribute:: deadline_handling

        An integer identifying how deadlines are handled.

            0
                Soft deadlines. Deliveries can be added until groups are closed.
            1
                Hard deadlines. Deliveries can not be added after the deadline
                has expired.

    .. attribute:: etag

        A DateTimeField containing the etag for this object.

    .. attribute:: first_deadline

        A DateTimeField containing an optional first deadline for this
        assignment. This is metadata that the UI can use where it is
        natural.

    .. attribute:: max_points

        An IntegerField that contains the maximum number of points possible to achieve on
        this assignment. This field may be ``None``, and it is normally set by the
        grading system plugin.

        DO NOT UPDATE MANUALLY. You can safely set an initial value for this 
        manually when you create a new assignment, but when you update this
        field, do so using :meth:`.set_max_points`.

    .. attribute:: passing_grade_min_points

        An IntegerField that contains the minimum number of points required to
        achive a passing grade on this assignment. This means that any feedback
        with more this number of points or more is considered a passing grade.

        WARNING: Changing this does not have any effect on existing feedback.
        To actually change existing feedback, you would have to update all
        feedback on the assignment, effectively creating new StaticFeedbacks
        from the latest published FeedbackDrafts for each AssignmentGroup.

    .. attribute:: points_to_grade_mapper

        Configures how points should be mapped to a grade. Valid choices:

        - ``passed-failed`` - Points is mapped directly to passed/failed.
          Zero points results in a failing grade, other points results in
          a passing grade.
        - ``raw-points`` - The grade is ``<points>/<max-points>``.
        - ``table-lookup`` - Points is mapped to a grade via a table lookup.
          This means that someone configures a mapping from point thresholds
          to grades using :class:`devilry.apps.core.models.PointRangeToGrade`.

    .. attribute:: grading_system_plugin_id

        A CharField containing the ID of the grading system plugin this
        assignment uses.
    """
    objects = AssignmentManager()

    DEADLINEHANDLING_SOFT = 0
    DEADLINEHANDLING_HARD = 1

    class Meta:
        app_label = 'core'
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']

    short_name = ShortNameField()
    long_name = LongNameField()
    parentnode = models.ForeignKey(Period, related_name='assignments',
                                   verbose_name='Period')
    etag = models.DateTimeField(auto_now_add=True)
    publishing_time = models.DateTimeField(
        verbose_name=_("Publishing time"),
        help_text=_('The time when the assignment is to be published (visible to students and examiners).'))
    anonymous = models.BooleanField(default=False,
        verbose_name=_("Anonymous?"),
        help_text=_(
            'On anonymous assignments, examiners and students can NOT see each other and '
            'they can NOT communicate. '
            'If an assignment is anonymous, examiners see candidate-id instead of any '
            'personal information about the students. '
            'This means that anonymous assignments is perfect for exams, and for assignments '
            'where you do not want prior experiences with a student to affect results.'))
    students_can_see_points = models.BooleanField(default=True,
            verbose_name="Students can see points")
    admins = models.ManyToManyField(User, blank=True,
            verbose_name="Administrators")
    examiners_publish_feedbacks_directly = models.BooleanField(default=True,
                                                     verbose_name="Examiners publish directly?",
                                                     help_text=('Should feedbacks published by examiners be made '
                                                                'avalable to the students immediately? If not, an '
                                                                'administrator have to publish feedbacks '
                                                                'manually.'))
    delivery_types = models.PositiveIntegerField(default=deliverytypes.ELECTRONIC,
                                                 choices=deliverytypes.as_choices_tuple(),
                                                 help_text='This option controls what types of deliveries this assignment accepts. See the Delivery documentation for more info.')
    deadline_handling = models.PositiveIntegerField(
        default=settings.DEFAULT_DEADLINE_HANDLING_METHOD,
        verbose_name=_('Deadline handling'),
        choices=(
            (DEADLINEHANDLING_SOFT, _('Soft deadlines')),
            (DEADLINEHANDLING_HARD, _('Hard deadlines'))
        ),
        help_text=_(
            'With HARD deadlines, students will be unable to make deliveries when a deadline has expired. '
            'With SOFT deadlines students will be able to make deliveries after the deadline '
            'has expired. All deliveries after their deadline are clearly highligted. '
            'NOTE: Devilry is designed from the bottom up to gracefully handle SOFT '
            'deadlines. Students have to perform an extra confirm-step when adding '
            'deliveries after their active deadline, and assignments where the deadline has '
            'expired is clearly marked for both students and examiners.'))
    scale_points_percent = models.PositiveIntegerField(default=100,
                                                       help_text='Percent to scale points on this assignment by for period overviews. The default is 100, which means no change to the points.')
    first_deadline = models.DateTimeField(blank=True, null=True)

    max_points = models.PositiveIntegerField(null=True, blank=True,
        verbose_name=_('Maximum points'),
        help_text=_('Specify the maximum number of points possible for this assignment.'),
        default=1)
    passing_grade_min_points = models.PositiveIntegerField(null=True, blank=True,
        default=1)
    points_to_grade_mapper = models.CharField(
        max_length=25, blank=True, null=True,
        default='passed-failed',
        choices=(
            ("passed-failed", _("As passed or failed")),
            ("raw-points", _("As points")),
            ("custom-table", _("As a text looked up in a custom table")),
        ))
    grading_system_plugin_id = models.CharField(
        default='devilry_gradingsystemplugin_approved',
        max_length=300, blank=True, null=True)


    @property
    def subject(self):
        return self.parentnode.parentnode

    @property
    def period(self):
        return self.parentnode


    def is_electronic(self):
        """
        Returns ``True`` if :attr:`.deliverytypes` is ``0`` (electric).

        .. versionadded:: 1.4.0
        """
        return self.delivery_types == deliverytypes.ELECTRONIC

    def is_nonelectronic(self):
        """
        Returns ``True`` if :attr:`.deliverytypes` is ``1`` (non-electric).

        .. versionadded:: 1.4.0
        """
        return self.delivery_types == deliverytypes.NON_ELECTRONIC

    def set_passing_grade_min_points(self, passing_grade_min_points):
        self.passing_grade_min_points = passing_grade_min_points

    def set_max_points(self, max_points):
        """
        Sets :attr:`.max_points`, and invalidates any
        :class:`~devilry.apps.core.models.PointToGradeMap` configured for this
        assignment if the new value for ``max_points`` differs from the old one.

        Invalidating the PointToGradeMap ensures that the course admin
        has to re-evaluate the grade to point mapping when they change ``max_points``.

        NOTE: This saves the PointToGradeMap, but not the assignment.
        """
        if self.max_points != max_points:
            self.max_points = max_points
            try:
                pointtogrademap = self.pointtogrademap
            except ObjectDoesNotExist:
                pass
            else:
                pointtogrademap.invalid = True
                pointtogrademap.save()
        if self.passing_grade_min_points > self.max_points:
            self.passing_grade_min_points = self.max_points

    def get_gradingsystem_plugin_api(self):
        """
        Shortcut for ``devilry_gradingsystem.pluginregistry.gradingsystempluginregistry.get(self.grading_system_plugin_id)(self)``.

        See: :meth:`devilry_gradingsystem.pluginregistry.GradingSystemPluginRegistry.get`.
        """
        ApiClass = gradingsystempluginregistry.get(self.grading_system_plugin_id)
        return ApiClass(self)

    def has_valid_grading_setup(self):
        """
        Checks if this assignment is configured correctly for grading.
        """
        if self.max_points is None \
                or self.passing_grade_min_points is None \
                or self.points_to_grade_mapper is None \
                or self.grading_system_plugin_id is None \
                or not self.grading_system_plugin_id in gradingsystempluginregistry:
            return False
        else:
            pluginapi = self.get_gradingsystem_plugin_api()
            if pluginapi.requires_configuration and not pluginapi.is_configured():
                return False
            if self.points_to_grade_mapper == 'custom-table':
                try:
                    pointtogrademap = self.pointtogrademap
                except ObjectDoesNotExist:
                    return False
                else:
                    return not pointtogrademap.invalid
            else:
                return True

    def setup_grading(self,
            grading_system_plugin_id, points_to_grade_mapper,
            passing_grade_min_points=None, max_points=None):
        """
        Setup all of the simple parts of the grading system:
        
        - :attr:`.grading_system_plugin_id`
        - :attr:`.points_to_grade_mapper`
        - :attr:`.passing_grade_min_points`
        - :attr:`.max_points`

        Does not setup:

        - Grading system plugin specific configuration.
        - A :class:`~devilry.apps.core.models.PointToGradeMap`.
        """
        self.grading_system_plugin_id = grading_system_plugin_id
        self.points_to_grade_mapper = points_to_grade_mapper
        pluginapi = self.get_gradingsystem_plugin_api()
        if pluginapi.sets_passing_grade_min_points_automatically:
            passing_grade_min_points = pluginapi.get_passing_grade_min_points()
        if pluginapi.sets_max_points_automatically:
            max_points = pluginapi.get_max_points()
        self.passing_grade_min_points = passing_grade_min_points
        self.max_points = max_points


    def get_point_to_grade_map(self):
        """
        Get the :class:`~devilry.apps.core.models.PointToGradeMap` for this assinment,
        creating if first if it does not exist.
        """
        from .pointrange_to_grade import PointToGradeMap
        try:
            pointtogrademap = self.pointtogrademap
        except ObjectDoesNotExist:
            pointtogrademap = PointToGradeMap.objects.create(
                assignment=self)
        return self.pointtogrademap



    def points_is_passing_grade(self, points):
        """
        Checks if the given points represents a passing grade.

        WARNING: This will only work if ``passing_grade_min_points`` is set. The best
        way to check that is with :meth:`.has_valid_grading_setup`.
        """
        return points >= self.passing_grade_min_points

    def points_to_grade(self, points):
        """
        Convert the given points into a grade.

        WARNING: This will not work if :meth:`.has_valid_grading_setup` is not ``True``.
        """
        if self.points_to_grade_mapper == 'passed-failed':
            if points == 0:
                return 'Failed'
            else:
                return 'Passed'
        elif self.points_to_grade_mapper == 'raw-points':
            return u'{}/{}'.format(points, self.max_points)
        else:
            return self.pointtogrademap.points_to_grade(points).grade


    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(publishing_time__lt=now)
        if not active:
            q &= ~Q(parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_candidate(cls, user_obj):
        return Q(assignmentgroups__candidates__student=user_obj)

    def save(self, *args, **kwargs):
        if self.pk:
            # Only when assignment already exists in the database
            self.update_candidates_identifer()
        super(Assignment, self).save(*args, **kwargs)

    def update_candidates_identifer(self):
        """ If the anonymous flag is changed, update the identifer on all
        the candidates on this assignment.
        """
        # Get current value stored in the db
        db_assignment = Assignment.objects.get(id=self.id)
        # No change, so return
        if self.anonymous == db_assignment.anonymous:
            return
        # Get all candidates on assignmentgroups for this assignment
        candidates = Candidate.objects.filter(Q(assignment_group__parentnode__id=self.id))
        for cand in candidates: 
            #cand.update_identifier(self.anonymous)
            cand.save(anonymous=self.anonymous)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(admins=user_obj) | \
                Q(parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__admins=user_obj) | \
                Q(parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(assignmentgroups__examiners__user=user_obj)

    def _clean_first_deadline(self):
        self.first_deadline = self.first_deadline.replace(microsecond=0, tzinfo=None) # NOTE: We want this so a unique deadline is a deadline which matches with second-specition.
        datetimeformat = '%Y-%m-%d %H:%M'
        if self.first_deadline < self.publishing_time:
            msg = _('Submission date can not be before the publishing time ({publishing_time}) of the assignment.')
            raise ValidationError(msg.format(publishing_time = self.publishing_time.strftime(datetimeformat)))
        if self.first_deadline > self.parentnode.end_time:
            msg = _("Submission date must be within it's {period_term} ({start_time} - {end_time}).")
            raise ValidationError(msg.format(period_term=_('period'),
                                             start_time=self.parentnode.start_time.strftime(datetimeformat),
                                             end_time=self.parentnode.end_time.strftime(datetimeformat)))

    def clean(self, *args, **kwargs):
        """Validate the assignment.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if ``publishing_time`` is not between
        :attr:`Period.start_time` and ``Period.end_time``.
        """
        super(Assignment, self).clean(*args, **kwargs)
        if self.publishing_time != None and self.parentnode_id != None:
            if self.publishing_time < self.parentnode.start_time  or \
                    self.publishing_time > self.parentnode.end_time:
                raise ValidationError(
                      _("The publishing time, {publishing_time}, is invalid. "
                        "It must be within it's period, {period}, "
                        "which lasts from {start_time} to {end_time}").format(publishing_time = self.publishing_time,
                                                                              period=unicode(self.parentnode),
                                                                              end_time=self.parentnode.end_time,
                                                                              start_time=self.parentnode.start_time))
        if self.first_deadline:
            self._clean_first_deadline()
        if self.passing_grade_min_points > self.max_points:
            raise ValidationError(
                _('The minumum number of points required to pass must be less than the maximum number of points possible on the assignment. The current maximum is {max_points}').format(
                    max_points=self.max_points))


    def is_empty(self):
        """
        Returns ``True`` if this Assignment does not contain any deliveries.
        """
        from .delivery import Delivery
        return Delivery.objects.filter(deadline__assignment_group__parentnode=self).count() == 0


    def is_active(self):
        """
        Returns ``True`` if this assignment is published, and the period has not ended yet.
        """
        now = datetime.now()
        return self.publishing_time < now and self.parentnode.end_time > now
