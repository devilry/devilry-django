import warnings
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.template import defaultfilters
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, pgettext_lazy, ugettext_lazy

from abstract_is_candidate import AbstractIsCandidate
from abstract_is_examiner import AbstractIsExaminer
from basenode import BaseNode
from custom_db_fields import ShortNameField, LongNameField
from devilry.apps.core.models.relateduser import RelatedStudentSyncSystemTag, RelatedExaminerSyncSystemTag
from devilry.devilry_account.models import User
from devilry.devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from node import Node
from period import Period
from . import deliverytypes


class AssignmentHasGroupsError(Exception):
    """
    Raised when performing an action that requires
    the assignment to not have any
    :class:`devilry.apps.core.models.AssignmentGroup`.
    """


class AssignmentQuerySet(models.QuerySet):
    """
    QuerySet for :class:`.Assignment`.
    """
    def filter_user_is_admin(self, user):
        """
        Filter the queryset to only include :class:`.Assignment` objects where the
        given ``user`` is in a :class:`.devilry.devilry_account.models.SubjectPermissionGroup`
        or in a :class:`.devilry.devilry_account.models.PeriodPermissionGroup`.

        Args:
            user: A User object.
        """
        periodids_where_is_admin_queryset = Period.objects\
            .filter_user_is_admin(user=user)\
            .values_list('id', flat=True)
        return self.filter(parentnode_id__in=periodids_where_is_admin_queryset)

    def filter_user_is_examiner(self, user):
        """
        Filter all :class:`.Assignment` objects where the given user is examiner.

        Args:
            user: A :class:`devilry.devilry_account.models.User` object.
        """
        return self.filter(assignmentgroups__examiners__relatedexaminer__user=user).distinct()

    def filter_user_is_candidate(self, user):
        """
        Filter :class:`.Assignment` objects where the given user is candidate.

        Args:
            user: A :class:`devilry.devilry_account.models.User` object.
        """
        return self.filter(assignmentgroups__candidates__relatedstudent__user=user).distinct()

    def filter_is_published(self):
        """
        Returns all active assignments (published assignments within a period that is currently started and not ended).
        """
        now = datetime.now()
        return self.filter(publishing_time__lt=now)

    def filter_is_active(self):
        """
        Returns all active assignments (published assignments within a period that is currently started and not ended).
        """
        now = datetime.now()
        return self.filter_is_published().filter(
            parentnode__start_time__lt=now,
            parentnode__end_time__gt=now)

    def filter_examiner_has_access(self, user):
        """
        Returns all assignments that the given ``user`` has access to as examiner.
        """
        return self.filter_is_active().filter_user_is_examiner(user)

    def filter_student_has_access(self, user):
        """
        Returns all assignments that the given ``user`` has access to as student.
        """
        return self.filter_is_published().filter_user_is_candidate(user)

    def filter_admin_has_access(self, user):
        if user.is_superuser:
            return self.all()
        else:
            return self.filter(Assignment.q_is_admin(user)).distinct()

    def annotate_with_waiting_for_feedback_count(self):
        """
        Annotate the queryset with ``waiting_for_feedback_count`` - the number
        of AssignmentGroups within the assignment that is waiting for feedback.

        Groups waiting for feedback is all groups where
        The deadline of the last feedbackset (or :attr:`.Assignment.first_deadline` and only one feedbackset)
        has expired, and the feedbackset does not have a
        :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`.
        """
        from devilry.devilry_group.models import FeedbackSet
        now = timezone.now()
        whenquery = models.Q(
            assignmentgroups__feedbackset__is_last_in_group=True,
            assignmentgroups__feedbackset__grading_published_datetime__isnull=True
        ) & (
            models.Q(assignmentgroups__feedbackset__deadline_datetime__lt=now) |
            models.Q(
                assignmentgroups__feedbackset__feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_TRY,
                first_deadline__lt=now
            )
        )

        return self.annotate(
            waiting_for_feedback_count=models.Count(
                models.Case(
                    models.When(whenquery, then=1)
                )
            )
        )


class Assignment(models.Model, BaseNode, AbstractIsExaminer, AbstractIsCandidate):
    """
    Data model for an assignment.

    .. attribute:: gradeform_setup_json

        A django.db.models.TextField_ for the json representing a blank
        gradeform used for this 'Assignment_'

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always a `Period`_.

    .. attribute:: publishing_time

        A django.db.models.DateTimeField_ representing the publishing time of
        the assignment.

    .. attribute:: admins

        A django.db.models.ManyToManyField_ that holds all the admins of the
        Node.

    .. attribute:: assignmentgroups

        A set of :class:`assignmentgroups <devilry.apps.core.models.AssignmentGroup>` for this assignment

    .. attribute:: scale_points_percent

        Percent to scale points on this assignment by for period overviews. The default is 100,
        which means no change to the points.

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


    .. attribute:: students_can_create_groups

        BooleanField specifying if students can join/leave groups on
        their own.

        If this is ``True`` students should be allowed to join/leave groups.
        If :attr:`.students_can_not_create_groups_after` is specified, this
        students can not create groups after ``students_can_not_create_groups_after``
        even if this is ``True``.

        This does not in any way affect an admins ability to organize students
        in groups manually.

    .. attribute:: students_can_not_create_groups_after

        Students can not create project groups after this time. Ignored if
        :attr:`.students_can_create_groups` is ``False``.

        DateTimeField that defaults to ``None`` (null).

    .. attribute:: feedback_workflow

        The feedback workflow used on the assignment. A feedback workflow
        defines how examiners and administrators work together to make
        feedback available to students.

        Introduced in :devilryissue:`765`.

    """
    objects = AssignmentQuerySet.as_manager()

    DEADLINEHANDLING_SOFT = 0
    DEADLINEHANDLING_HARD = 1

    class Meta:
        app_label = 'core'
        unique_together = ('short_name', 'parentnode')
        ordering = ['short_name']
        verbose_name = _('assignment')
        verbose_name_plural = _('assignments')

    short_name = ShortNameField()
    long_name = LongNameField()
    gradeform_setup_json = models.TextField(blank=True, null=True)
    parentnode = models.ForeignKey(Period, related_name='assignments',
                                   verbose_name='Period')
    publishing_time = models.DateTimeField(
        verbose_name=_("Publishing time"),
        help_text=_('The time when the assignment is to be published (visible to students and examiners).'))

    #: Deprecated anonymous field.
    #: Will be removed in 3.1.
    deprecated_field_anonymous = models.BooleanField(
        default=False,
        verbose_name="Anonymous? (deprectated field)",
        editable=False,
        help_text='Deprecated anonymous field. Will be removed in 3.1.')

    #: If this is set to ``True``, the assignment manages its own set of candidate IDs,
    #: and candidate IDs from the semester is ignored. Candidate IDs for an assignment
    #: using ``uses_custom_candate_ids=True`` is stored in
    #: :obj:`devilry.apps.core.models.candidate.Candidate.candidate_id`.
    # Candidate IDs for an assignment using ``uses_custom_candate_ids=False`` (the default)
    # is stored in :obj:`devilry.apps.core.models.relateduser.RelatedStudent.candidate_id`.
    uses_custom_candidate_ids = models.BooleanField(
        default=False,
        help_text='If this is enabled, the assignment does not inherit candidate IDs '
                  'from the semester, and instead have their own set of candidate IDs '
                  'only for this assignment.'
    )

    #: Constant for the :obj:`~.Assignment.anonymizationmode` "off" choice.
    ANONYMIZATIONMODE_OFF = 'off'

    #: Constant for the :obj:`~.Assignment.anonymizationmode` "semi_anonymous" choice.
    ANONYMIZATIONMODE_SEMI_ANONYMOUS = 'semi_anonymous'

    #: Constant for the :obj:`~.Assignment.anonymizationmode` "fully_anonymous" choice.
    ANONYMIZATIONMODE_FULLY_ANONYMOUS = 'fully_anonymous'

    #: Choices for :obj:`~.Assignment.anonymizationmode`.
    ANONYMIZATIONMODE_CHOICES = [
        (
            ANONYMIZATIONMODE_OFF,
            pgettext_lazy('assignment anonymizationmode',
                          'OFF. Normal assignment where semester and course admins can see everything, '
                          'and examiners and students can see each others names and contact information.')
        ),
        (
            ANONYMIZATIONMODE_SEMI_ANONYMOUS,
            pgettext_lazy('assignment anonymizationmode',
                          'SEMI ANONYMOUS. Students and examiners can not see information about each other. '
                          'Comments added by course admins are not anonymized. '
                          'Semester admins do not have access to the assignment in the admin UI. Course admins '
                          'have the same permissions as for "OFF".')
        ),
        (
            ANONYMIZATIONMODE_FULLY_ANONYMOUS,
            pgettext_lazy('assignment anonymizationmode',
                          'FULLY ANONYMIZED. Intended for exams where course admins are examiners. '
                          'Students and examiners can not see information about each other. Hidden '
                          'from semester admins. Course admins can not view grading details. Only '
                          'departmentadmins and superusers can change this back to another "anoymization mode" '
                          'when feedback has been added to the assignment. Course admins can not edit '
                          'examiners after the first feedback is provided.')
        ),
    ]

    #: A choicefield that specifies how the assignment is anonymized (or not).
    #:
    #: Choices:
    #:
    #: - ``"off"``: Normal assignment where semester and course admins can see everything,
    #:   and examiners and students can see each others names and contact information.
    #: - ``"semi_anonymous"``: Students and examiners
    #:   can not see information about each other. Semester admins can not view the
    #:   assignment at all. Course admins have the same permissions as for ``"off"``.
    #: - ``"fully_anonymous"``: Students and examiners
    #:   can not see information about each other. Course admins can not view results
    #:   (or AssignmentGroup.id). Hidden from semester admins. Can not be changed unless
    #:   you are member of a group with ``grouptype="departmentadmin"`` and has access to
    #:   the assignment. Course admins can not edit examiners after the first feedback is provided.
    anonymizationmode = models.CharField(
        verbose_name=ugettext_lazy('Anonymization mode'),
        max_length=15,
        choices=ANONYMIZATIONMODE_CHOICES,
        default=ANONYMIZATIONMODE_OFF,
        db_index=True
    )

    students_can_see_points = models.BooleanField(
        default=True,
        verbose_name="Students can see points")
    admins = models.ManyToManyField(User, blank=True, verbose_name="Administrators")
    delivery_types = models.PositiveIntegerField(
        default=deliverytypes.ELECTRONIC,
        choices=deliverytypes.as_choices_tuple(),
        help_text=('This option controls what types of deliveries this '
                   'assignment accepts. See the Delivery documentation '
                   'for more info.'))
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
    scale_points_percent = models.PositiveIntegerField(
        default=100,
        help_text=('Percent to scale points on this assignment by for '
                   'period overviews. The default is 100, which means '
                   'no change to the points.'))
    first_deadline = models.DateTimeField(blank=True, null=True)

    max_points = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name=_('Maximum points'),
        help_text=_('Specify the maximum number of points possible for this assignment.'),
        default=1)
    passing_grade_min_points = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name=_('Minumum number of points required to pass'),
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

    students_can_create_groups = models.BooleanField(
        default=False,
        verbose_name=_(u'Students can create project groups?'),
        help_text=_(u'Select this if students should be allowed to join/leave groups. '
                    u'Even if this is not selected, you can still organize your students '
                    u'in groups manually.'))
    students_can_not_create_groups_after = models.DateTimeField(
        default=None, null=True, blank=True,
        verbose_name=_(u'Students can not create project groups after'),
        help_text=_(u'Students can not create project groups after this time. '
                    u'Ignored if "Students can create project groups" is not selected.'))

    feedback_workflow = models.CharField(
        blank=True, null=False, default='', max_length=50,
        verbose_name=_('Feedback workflow'),
        choices=(
            ('',
             _('Simple - Examiners write feedback, and publish it whenever '
               'they want. Does not handle coordination of multiple examiners at all.')),
            ('trusted-cooperative-feedback-editing',
             _('Trusted cooperative feedback editing - Examiners can only save feedback drafts. '
               'Examiners share the same feedback drafts, which means that one examiner can '
               'start writing feedback and another can continue. '
               'When an administrator is notified by their examiners that they have finished '
               'correcting, they can publish the drafts via the administrator UI. '
               'If you want one examiner to do the bulk of the work, and just let another '
               'examiner read it over and adjust the feedback, make the first examiner '
               'the only examiner, and reassign the students to the other examiner when '
               'the first examiner is done.')),
        )
    )

    @property
    def subject(self):
        return self.parentnode.parentnode

    @property
    def period(self):
        return self.parentnode

    @property
    def is_anonymous(self):
        """
        Returns ``True`` if ``anonymizationmode != "off"``.
        """
        return self.anonymizationmode != self.ANONYMIZATIONMODE_OFF

    @property
    def students_can_create_groups_now(self):
        """
        Return ``True`` if :attr:`students_can_create_groups` is ``True``, and
        :attr:`students_can_not_create_groups_after` is in the future or ``None``.
        """
        return self.students_can_create_groups and (
            self.students_can_not_create_groups_after is None or
            self.students_can_not_create_groups_after > datetime.now())

    def students_must_be_anonymized_for_devilryrole(self, devilryrole):
        """
        Check if students must be anonymized for the given ``devilryrole``.

        Args:
            devilryrole: Must be one of ``"student"``, ``"examiner"``, ``"periodadmin"``,
                ``"subjectadmin"`` or ``"departmentadmin"``.
                This is used to determine if candidates needs to be anonymized or not
                using the following rules:

                - If devilryrole is ``"student"``, candidates do not need to be anonymized even
                  if the assignment is anonymous.
                - If devilryrole is ``"examiner"``, candidates need to be anonymized if the assignment
                  is anonymous.
                - If devilryrole is ``"periodadmin"``, candidates need to be anonymized if the assignment
                  is anonymous.
                - If devilryrole is ``"subjectadmin"``, candidates need to be
                  anonymized if the assignment is anonymized with ``anonymizationmode="fully_anonymous"``.
                - If devilryrole is ``"departmentadmin"``, candidates do not need to be anonymized even
                  if the assignment is anonymous.

        Returns:
            bool: ``True`` if the candidates must be anonymized for the given role.
        """
        if devilryrole == 'student':
            return False
        elif devilryrole == 'examiner':
            return self.is_anonymous
        elif devilryrole == 'periodadmin':
            return self.is_anonymous
        elif devilryrole == 'subjectadmin':
            return self.anonymizationmode == self.ANONYMIZATIONMODE_FULLY_ANONYMOUS
        elif devilryrole == 'departmentadmin':
            return False
        else:
            raise ValueError('{} is an invalid value for devilryrole.'.format(devilryrole))

    def examiners_must_be_anonymized_for_devilryrole(self, devilryrole):
        """
        Check if examiners must be anonymized for the given ``devilryrole``.

        Args:
            devilryrole: Must be one of ``"student"``, ``"examiner"``, ``"periodadmin"``,
                ``"subjectadmin"`` or ``"departmentadmin"``.
                This is used to determine if examiners needs to be anonymized or not
                using the following rules:

                - If devilryrole is ``"student"``, examiners need to be anonymized if the assignment
                  is anonymous.
                - If devilryrole is ``"examiner"``, examiners do not need to be anonymized even
                  if the assignment is anonymous.
                - If devilryrole is ``"periodadmin"``, examiners need to be anonymized if the assignment
                  is anonymous.
                - If devilryrole is ``"subjectadmin"``, examiners need to be
                  anonymized if the assignment is anonymized with ``anonymizationmode="fully_anonymous"``.

        Returns:
            bool: ``True`` if the examiners must be anonymized for the given role.
        """
        if devilryrole == 'student':
            return self.is_anonymous
        elif devilryrole == 'examiner':
            return False
        elif devilryrole == 'periodadmin':
            return self.is_anonymous
        elif devilryrole == 'subjectadmin':
            return self.anonymizationmode == self.ANONYMIZATIONMODE_FULLY_ANONYMOUS
        elif devilryrole == 'departmentadmin':
            return False
        else:
            raise ValueError('{} is an invalid value for devilryrole.'.format(devilryrole))

    def feedback_workflow_allows_shared_feedback_drafts(self):
        """
        Return ``True`` if the :attr:`feedback_workflow` allows examiners to access
        each others feedback drafts.
        """
        return self.feedback_workflow == 'trusted-cooperative-feedback-editing'

    def feedback_workflow_allows_examiners_publish_feedback(self):
        """
        Return ``True`` if the :attr:`feedback_workflow` allows examiners to publish
        feedback.
        """
        return self.feedback_workflow != 'trusted-cooperative-feedback-editing'

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
        Shortcut for::

            devilry.devilry_gradingsystem.pluginregistry.gradingsystempluginregistry.get(
                self.grading_system_plugin_id)(self)

        See: :meth:`devilry.devilry_gradingsystem.pluginregistry.GradingSystemPluginRegistry.get`.
        """
        apiclass = gradingsystempluginregistry.get(self.grading_system_plugin_id)
        return apiclass(self)

    def has_valid_grading_setup(self):
        """
        Checks if this assignment is configured correctly for grading.
        """
        if self.max_points is None \
                or self.passing_grade_min_points is None \
                or self.points_to_grade_mapper is None \
                or self.grading_system_plugin_id is None \
                or self.grading_system_plugin_id not in gradingsystempluginregistry:
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

    def setup_grading(
            self, grading_system_plugin_id, points_to_grade_mapper,
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
            return self.pointtogrademap
        except ObjectDoesNotExist:
            self.pointtogrademap = PointToGradeMap.objects.create(
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
        warnings.warn("deprecated", DeprecationWarning)
        now = datetime.now()
        q = Q(publishing_time__lt=now)
        if not active:
            q &= ~Q(parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_candidate(cls, user_obj):
        warnings.warn("deprecated", DeprecationWarning)
        return Q(assignmentgroups__candidates__student=user_obj)

    @classmethod
    def q_is_admin(cls, user_obj):
        warnings.warn("deprecated", DeprecationWarning)
        return \
            Q(admins=user_obj) | \
            Q(parentnode__admins=user_obj) | \
            Q(parentnode__parentnode__admins=user_obj) | \
            Q(parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def q_is_examiner(cls, user_obj):
        warnings.warn("deprecated", DeprecationWarning)
        return Q(assignmentgroups__examiners__user=user_obj)

    def _clean_first_deadline(self, errors):
        # NOTE: We want this so a unique deadline is a deadline which matches with second-specition.
        self.first_deadline = self.first_deadline.replace(microsecond=0, tzinfo=None)

        if self.first_deadline > self.parentnode.end_time or self.first_deadline < self.parentnode.start_time:
            errors['first_deadline'] = _("First deadline must be within %(periodname)s, "
                                         "which lasts from %(start_time)s to %(end_time)s.") % {
                'periodname': self.parentnode.long_name,
                'start_time': defaultfilters.date(self.parentnode.start_time,
                                                  'DATETIME_FORMAT'),
                'end_time': defaultfilters.date(self.parentnode.end_time, 'DATETIME_FORMAT')
            }

    def clean(self):
        """Validate the assignment.

        Always call this before save()! Read about validation here:
        http://docs.djangoproject.com/en/dev/ref/models/instances/#id1

        Raises ValidationError if ``publishing_time`` is not between
        :attr:`Period.start_time` and ``Period.end_time``.
        """
        super(Assignment, self).clean()
        errors = {}
        if self.publishing_time is not None and self.parentnode_id is not None:
            if self.publishing_time < self.parentnode.start_time or self.publishing_time > self.parentnode.end_time:
                errors['publishing_time'] = _("Publishing time must be within %(periodname)s, "
                                              "which lasts from %(start_time)s to %(end_time)s.") % {
                    'periodname': self.parentnode.long_name,
                    'start_time': defaultfilters.date(self.parentnode.start_time,
                                                      'DATETIME_FORMAT'),
                    'end_time': defaultfilters.date(self.parentnode.end_time,
                                                    'DATETIME_FORMAT')
                }
        if self.first_deadline:
            self._clean_first_deadline(errors)
        if self.passing_grade_min_points > self.max_points:
            errors['passing_grade_min_points'] = _('The minumum number of points required to pass must be less than '
                                                   'the maximum number of points possible for the assignment. The '
                                                   'current maximum is %(max_points)s.') % {
                'max_points': self.max_points
            }

        if errors:
            raise ValidationError(errors)

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
        warnings.warn("deprecated", DeprecationWarning)
        now = datetime.now()
        return self.publishing_time < now and self.parentnode.end_time > now

    def deadline_handling_is_hard(self):
        return self.deadline_handling == self.DEADLINEHANDLING_HARD

    def copy_groups_from_another_assignment(self, sourceassignment):
        """
        Copy all AssignmentGroup objects from another assignment.

        Copies:

        - The name of the group.
        """
        from devilry.apps.core.models import AssignmentGroup
        from devilry.apps.core.models import Candidate
        from devilry.apps.core.models import Examiner

        if self.assignmentgroups.exists():
            raise AssignmentHasGroupsError(_('The assignment has students. You can not '
                                             'copy use this on assignments with students.'))

        # Step1: Bulk create the groups with no candidates or examiners, but set copied_from.
        groups = []
        for othergroup in sourceassignment.assignmentgroups.all():
            newgroup = AssignmentGroup(parentnode=self,
                                       name=othergroup.name,
                                       copied_from=othergroup)
            groups.append(newgroup)
        AssignmentGroup.objects.bulk_create(groups)

        # Step2: Bulk create candidate and examiners from group.copied_from.<candidates|examiners>.
        candidates = []
        examiners = []

        for group in self.assignmentgroups \
                .prefetch_related(
                    models.Prefetch(
                        'copied_from',
                        to_attr='copied_from_list',
                        queryset=AssignmentGroup.objects.prefetch_related(
                            models.Prefetch('candidates',
                                            to_attr='candidatelist',
                                            queryset=Candidate.objects.all()),
                            models.Prefetch('examiners',
                                            to_attr='examinerlist',
                                            queryset=Examiner.objects.all()),
                        )
                    )
                ):
            for othercandidate in group.copied_from_list.candidatelist:
                newcandidate = Candidate(
                    assignment_group=group,
                    relatedstudent_id=othercandidate.relatedstudent_id,
                )
                candidates.append(newcandidate)
            for otherexaminer in group.copied_from_list.examinerlist:
                newexaminer = Examiner(
                    assignmentgroup=group,
                    user_id=otherexaminer.user_id
                )
                examiners.append(newexaminer)
        Candidate.objects.bulk_create(candidates)
        Examiner.objects.bulk_create(examiners)

    def create_groups_from_relatedstudents_on_period(self):
        """
        Create :class:`devilry.apps.core.models.AssignmentGroup` objects
        for all :class:`devilry.apps.core.models.RelatedStudent` objects
        on the period owning this assignment.

        Creates one AssignmentGroup for each RelatedStudent, with a
        single Candidate in each AssignmentGroup.
        """
        from devilry.apps.core.models import AssignmentGroup
        from devilry.apps.core.models import Candidate

        if self.assignmentgroups.exists():
            raise AssignmentHasGroupsError(_('The assignment has students. You can not '
                                             'copy use this on assignments with students.'))

        # We iterate over relatedstudents twice, so we
        # use this to avoid multiple queries
        relatedstudents = list(self.period.relatedstudent_set.all())

        # Step1: Bulk create empty groups
        groups = []
        for relatedstudent in relatedstudents:
            newgroup = AssignmentGroup(parentnode=self)
            groups.append(newgroup)
        AssignmentGroup.objects.bulk_create(groups)

        # Step2: Bulk create candidates
        candidates = []
        for group, relatedstudent in zip(self.assignmentgroups.all(), relatedstudents):
            candidate = Candidate(
                assignment_group=group,
                relatedstudent=relatedstudent)
            candidates.append(candidate)
        Candidate.objects.bulk_create(candidates)

    def setup_examiners_by_relateduser_syncsystem_tags(self):
        from devilry.apps.core.models import Candidate
        from devilry.apps.core.models import Examiner
        period = self.period

        # We use this to avoid adding examiners to groups they are already on
        # We could have used an exclude query, but this is more efficien because
        # it only requires one query.
        groupid_to_examineruserid_map = dict(Examiner.objects.filter(
            assignmentgroup__parentnode=self).values_list('assignmentgroup_id', 'user_id'))

        # We collect all the examiners to be created in this list, and bulk create
        # them at the end
        examinerobjects = []

        for relatedexaminer_syncsystem_tag in RelatedExaminerSyncSystemTag.objects\
                .filter(relatedexaminer__period=period)\
                .select_related('relatedexaminer__user'):

            # Step1: Collect all relatedstudents with same tag as examiner
            relatedstudentids = []
            for relatedstudent_syncsystem_tag in RelatedStudentSyncSystemTag.objects\
                    .filter(relatedstudent__period=period,
                            tag=relatedexaminer_syncsystem_tag.tag):
                relatedstudentids.append(relatedstudent_syncsystem_tag.relatedstudent_id)

            # Step2: Find the group of all the students matching the tag
            #        and bulk create Examiner objects for the groups
            #        if the user is not already examiner.
            if relatedstudentids:
                examineruser = relatedexaminer_syncsystem_tag.relatedexaminer.user
                groupids = set()
                for candidate in Candidate.objects\
                        .filter(assignment_group__parentnode=self,
                                relatedstudent_id__in=relatedstudentids)\
                        .distinct():
                    if groupid_to_examineruserid_map.get(candidate.assignment_group_id, None) != examineruser.id:
                        groupids.add(candidate.assignment_group_id)

                examinerobjects.extend([Examiner(
                    assignmentgroup_id=groupid,
                    user=examineruser
                ) for groupid in groupids])
        if examinerobjects:
            Examiner.objects.bulk_create(examinerobjects)
