import warnings
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.template import defaultfilters
from django.utils import timezone
from django.utils.translation import gettext_lazy, pgettext_lazy

from .abstract_is_candidate import AbstractIsCandidate
from .abstract_is_examiner import AbstractIsExaminer
from .basenode import BaseNode
from .custom_db_fields import ShortNameField, LongNameField
from devilry.apps.core.models import RelatedStudent
from devilry.devilry_account.models import User, PeriodPermissionGroup
from devilry.devilry_gradingsystem.pluginregistry import gradingsystempluginregistry
from .period import Period
from .subject import Subject
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
        if user.is_superuser:
            return self.all()
        else:
            subjectids_where_is_admin_queryset = Subject.objects \
                .filter_user_is_admin(user=user) \
                .values_list('id', flat=True)
            periodids_where_is_admin_queryset = PeriodPermissionGroup.objects \
                .filter(models.Q(permissiongroup__users=user)) \
                .values_list('period_id', flat=True)
            return self.filter(
                # If anonymous, ignore periodadmins
                models.Q(
                    models.Q(
                        models.Q(anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS) |
                        models.Q(anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
                    ) &
                    models.Q(parentnode__parentnode_id__in=subjectids_where_is_admin_queryset)
                ) |

                # If not anonymous, include periodadmins
                models.Q(
                    models.Q(anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF) &
                    models.Q(
                        models.Q(parentnode_id__in=periodids_where_is_admin_queryset) |
                        models.Q(parentnode__parentnode_id__in=subjectids_where_is_admin_queryset)
                    )
                )
            )

    def filter_user_is_examiner(self, user):
        """
        Filter all :class:`.Assignment` objects where the given user is examiner.

        .. warning:: **Do not** use this to filter assignments where an
            examiner has access. Use :meth:`.filter_examiner_has_access`.

        Args:
            user: A User object.
        """
        return self \
            .filter(assignmentgroups__examiners__relatedexaminer__user=user,
                    assignmentgroups__examiners__relatedexaminer__active=True) \
            .distinct()

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
        now = timezone.now()
        return self.filter(publishing_time__lt=now)

    def filter_is_active(self):
        """
        Returns all active assignments (published assignments within a period that is currently started and not ended).
        """
        now = timezone.now()
        return self.filter_is_published().filter(
            parentnode__start_time__lt=now,
            parentnode__end_time__gt=now)

    def filter_examiner_has_access(self, user):
        """
        Returns all assignments that the given ``user`` has access to as examiner.

        Args:
            user: A User object.
        """
        return self.filter_is_active() \
            .filter(assignmentgroups__examiners__relatedexaminer__user=user,
                    assignmentgroups__examiners__relatedexaminer__active=True)

    def filter_student_has_access(self, user):
        """
        Returns all assignments that the given ``user`` has access to as student.
        """
        return self.filter_is_published().filter_user_is_candidate(user)

    def annotate_with_waiting_for_feedback_count(self):
        """
        Annotate the queryset with ``waiting_for_feedback_count`` - the number
        of AssignmentGroups within the assignment that is waiting for feedback.

        Groups waiting for feedback is all groups where
        The deadline of the last feedbackset (or :attr:`.Assignment.first_deadline` and only one feedbackset)
        has expired, and the last feedbackset does not have a
        :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`.
        """
        now = timezone.now()
        whenquery = models.Q(
            assignmentgroups__cached_data__last_feedbackset__grading_published_datetime__isnull=True
        ) & (
                            models.Q(
                                ~models.Q(assignmentgroups__cached_data__last_feedbackset=models.F(
                                    'assignmentgroups__cached_data__first_feedbackset')),
                                models.Q(assignmentgroups__cached_data__last_feedbackset__deadline_datetime__lt=now),
                            ) |
                            models.Q(
                                models.Q(assignmentgroups__cached_data__last_feedbackset=models.F(
                                    'assignmentgroups__cached_data__first_feedbackset')),
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

    def prefetch_point_to_grade_map(self):
        """
        Prefetches the :class:`devilry.apps.core.models.PointToGradeMap` for each
        assignment in the queryset.

        Adds the ``prefetched_point_to_grade_map`` attribute to each assignment
        in the queryset:

            If there is no PointToGradeMap for the assignment,
            the attribute will be ``None``.

            If there is a PointToGradeMap for the assignment,
            the attribute will be a :class:`devilry.apps.core.models.PointToGradeMap`
            object. This object will have class:`devilry.apps.core.models.PointRangeToGrade`
            prefetched and ordered.
        """
        from .pointrange_to_grade import PointToGradeMap
        return self.prefetch_related(
            models.Prefetch('pointtogrademap',
                            queryset=PointToGradeMap.objects.prefetch_pointrange_to_grade(),
                            to_attr='prefetched_point_to_grade_map'))


def get_deadline_handling_default():
    return settings.DEFAULT_DEADLINE_HANDLING_METHOD


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

    .. attribute:: grading_system_plugin_id

        A CharField containing the ID of the grading system plugin this
        assignment uses.


    .. attribute:: students_can_create_groups

        BooleanField specifying if students can join/leave groups on
        their own.

        If this is ``True`` students should be allowed to join/leave groups.
        If :attr:`.students_can_not_create_groups_after` is specified, this
        students can not create groups after ``students_can_not_create_groups_after``
        even if this is ``True``.ar 16 2017, 17:45 : This delivery was corrected, and given:

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
        verbose_name = gettext_lazy('assignment')
        verbose_name_plural = gettext_lazy('assignments')

    short_name = ShortNameField()
    long_name = LongNameField()
    gradeform_setup_json = models.TextField(blank=True, null=True)
    parentnode = models.ForeignKey(Period, related_name='assignments',
                                   verbose_name='Period',
                                   on_delete=models.CASCADE)
    publishing_time = models.DateTimeField(
        verbose_name=gettext_lazy("Publishing time"),
        help_text=gettext_lazy('The time when the assignment is to be published (visible to students and examiners).'))

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

    #: Dictionary for getting the :obj:`~.Assignment.ANONYMIZATIONMODE_CHOICES` descriptions
    ANONYMIZATIONMODE_CHOICES_DICT = dict(ANONYMIZATIONMODE_CHOICES)

    #: Dictionary mapping :obj:`.Assignment.anonymizationmode` choices to short
    #: labels.
    ANONYMIZATIONMODE_CHOICES_SHORT_LABEL_DICT = {
        ANONYMIZATIONMODE_OFF: pgettext_lazy(
            'assignment anonymizationmode', 'off'),
        ANONYMIZATIONMODE_SEMI_ANONYMOUS: pgettext_lazy(
            'assignment anonymizationmode', 'semi anonymous'),
        ANONYMIZATIONMODE_FULLY_ANONYMOUS: pgettext_lazy(
            'assignment anonymizationmode', 'fully anonymized'),
    }

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
        verbose_name=gettext_lazy('Anonymization mode'),
        max_length=15,
        choices=ANONYMIZATIONMODE_CHOICES,
        default=ANONYMIZATIONMODE_OFF,
        db_index=True
    )

    students_can_see_points = models.BooleanField(
        default=False,
        verbose_name=pgettext_lazy(
            'assignment',
            "Students can see points?"))
    admins = models.ManyToManyField(User, blank=True, verbose_name="Administrators")
    delivery_types = models.PositiveIntegerField(
        default=deliverytypes.ELECTRONIC,
        choices=deliverytypes.as_choices_tuple(),
        help_text=gettext_lazy('This option controls what types of deliveries this '
                    'assignment accepts. See the Delivery documentation '
                    'for more info.'))
    deadline_handling = models.PositiveIntegerField(
        default=get_deadline_handling_default,
        verbose_name=gettext_lazy('Deadline handling'),
        choices=(
            (DEADLINEHANDLING_SOFT, gettext_lazy('Soft deadlines')),
            (DEADLINEHANDLING_HARD, gettext_lazy('Hard deadlines'))
        ),
        help_text=gettext_lazy(
            'With HARD deadlines, students will be unable to make deliveries when a deadline has expired. '
            'With SOFT deadlines students will be able to make deliveries after the deadline '
            'has expired. All deliveries after their deadline are clearly highligted. '
            'NOTE: Devilry is designed from the bottom up to gracefully handle SOFT '
            'deadlines. Students have to perform an extra confirm-step when adding '
            'deliveries after their active deadline, and assignments where the deadline has '
            'expired is clearly marked for both students and examiners.'))
    scale_points_percent = models.PositiveIntegerField(
        default=100,
        help_text=gettext_lazy('Percent to scale points on this assignment by for '
                    'period overviews. The default is 100, which means '
                    'no change to the points.'))
    first_deadline = models.DateTimeField(blank=False, null=False)

    max_points = models.PositiveIntegerField(
        null=True, blank=True,
        default=1)
    passing_grade_min_points = models.PositiveIntegerField(
        null=True, blank=True,
        default=1)

    #: The "passed-or-failed" value for :obj:`~.Assignment.points_to_grade_mapper`.
    #: Zero points results in a failing grade, other points results in a passing grade.
    POINTS_TO_GRADE_MAPPER_PASSED_FAILED = 'passed-failed'

    #: The "raw-points" value for :obj:`~.Assignment.points_to_grade_mapper`.
    #: The grade is ``<points>/<max-points>``.
    POINTS_TO_GRADE_MAPPER_RAW_POINTS = 'raw-points'

    #: The "custom-table" value for :obj:`~.Assignment.points_to_grade_mapper`.
    #: For this choice, someone configures a mapping from point thresholds
    #: to grades using :class:`devilry.apps.core.models.PointRangeToGrade`.
    POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE = 'custom-table'

    #: Choices for :obj:`~.Assignment.points_to_grade_mapper`
    POINTS_TO_GRADE_MAPPER_CHOICES = [
        (
            POINTS_TO_GRADE_MAPPER_PASSED_FAILED,
            pgettext_lazy('assignment points-to-grade mapper',
                          'Passed or failed')
        ),
        (
            POINTS_TO_GRADE_MAPPER_RAW_POINTS,
            pgettext_lazy('assignment points-to-grade mapper',
                          'Points')
        ),
        (
            POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE,
            pgettext_lazy('assignment points-to-grade mapper',
                          'Lookup in a table defined by you (A-F, and other grading systems)')
        ),
    ]
    #: Dictionary for getting the :obj:`~.Assignment.POINTS_TO_GRADE_MAPPER_CHOICES` descriptions
    POINTS_TO_GRADE_MAPPER_CHOICES_DICT = dict(POINTS_TO_GRADE_MAPPER_CHOICES)

    #: Points to grade mapper. Defines how we map points to a grade.
    #: Choices are:
    #:
    #: - :obj:`~.Assignment.POINTS_TO_GRADE_MAPPER_PASSED_FAILED` (default value)
    #: - :obj:`~.Assignment.POINTS_TO_GRADE_MAPPER_RAW_POINTS`
    #: - :obj:`~.Assignment.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE`
    points_to_grade_mapper = models.CharField(
        max_length=25, blank=True, null=True,
        default=POINTS_TO_GRADE_MAPPER_PASSED_FAILED,
        choices=POINTS_TO_GRADE_MAPPER_CHOICES)

    GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED = 'devilry_gradingsystemplugin_approved'
    GRADING_SYSTEM_PLUGIN_ID_POINTS = 'devilry_gradingsystemplugin_points'
    # GRADING_SYSTEM_PLUGIN_ID_SCHEMA = 'schema'
    GRADING_SYSTEM_PLUGIN_ID_CHOICES = [
        (
            GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED,
            pgettext_lazy(
                'assignment grading plugin',
                'PASSED/FAILED. The examiner selects passed or failed.')
        ),
        (
            GRADING_SYSTEM_PLUGIN_ID_POINTS,
            pgettext_lazy(
                'assignment grading plugin',
                'POINTS. The examiner types in the number of points to award the '
                'student(s) for this assignment.')
        ),
        # (
        #     GRADING_SYSTEM_PLUGIN_ID_SCHEMA,
        #     pgettext_lazy(
        #         'assignment grading plugin',
        #         'SCHEMA. The examiner fill in a schema defined by you.')
        # )
    ]

    #: Dictionary for getting the :obj:`~.Assignment.GRADING_SYSTEM_PLUGIN_ID_CHOICES` descriptions
    GRADING_SYSTEM_PLUGIN_ID_CHOICES_DICT = dict(GRADING_SYSTEM_PLUGIN_ID_CHOICES)

    #: Grading system plugin ID. Defines how examiners grade the students.
    grading_system_plugin_id = models.CharField(
        default=GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED,
        max_length=300, blank=True, null=True,
        choices=GRADING_SYSTEM_PLUGIN_ID_CHOICES)

    students_can_create_groups = models.BooleanField(
        default=False,
        verbose_name=gettext_lazy('Students can create project groups?'),
        help_text=gettext_lazy('Select this if students should be allowed to join/leave groups. '
                    'Even if this is not selected, you can still organize your students '
                    'in groups manually.'))
    students_can_not_create_groups_after = models.DateTimeField(
        default=None, null=True, blank=True,
        verbose_name=gettext_lazy('Students can not create project groups after'),
        help_text=gettext_lazy('Students can not create project groups after this time. '
                    'Ignored if "Students can create project groups" is not selected.'))

    feedback_workflow = models.CharField(
        blank=True, null=False, default='', max_length=50,
        verbose_name=gettext_lazy('Feedback workflow'),
        choices=(
            ('',
             gettext_lazy('Simple - Examiners write feedback, and publish it whenever '
               'they want. Does not handle coordination of multiple examiners at all.')),
            ('trusted-cooperative-feedback-editing',
             gettext_lazy('Trusted cooperative feedback editing - Examiners can only save feedback drafts. '
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

    examiners_can_self_assign = models.BooleanField(
        default=False,
        verbose_name=gettext_lazy('Can examiners assign themselves to the assignment?'),
        help_text=gettext_lazy('Select this if you want examiners to be able to self-assign to the assignment.')
    )
    examiner_self_assign_limit = models.PositiveIntegerField(
        default=1,
        help_text=gettext_lazy('The max number of examiners that are allowed '
            'to self-assign to each project group within the assignment.')
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
    def is_semi_anonymous(self):
        """
        Returns ``True`` if ``anonymizationmode == "semi_anonymous"``.
        """
        return self.anonymizationmode == self.ANONYMIZATIONMODE_SEMI_ANONYMOUS

    @property
    def is_fully_anonymous(self):
        """
        Returns ``True`` if ``anonymizationmode == "semi_anonymous"``.
        """
        return self.anonymizationmode == self.ANONYMIZATIONMODE_FULLY_ANONYMOUS

    @property
    def publishing_time_is_in_future(self):
        """
        Returns ``True`` if ``publishing_time`` is in the future.
        """
        if self.publishing_time > timezone.now():
            return True
        return False

    @property
    def is_published(self):
        """
        Returns ``True`` if ``publishing_time`` is in the past.
        """
        if self.publishing_time < timezone.now():
            return True
        return False

    @property
    def students_can_create_groups_now(self):
        """
        Returns ``True`` if :attr:`students_can_create_groups` is ``True``, and
        :attr:`students_can_not_create_groups_after` is in the future or ``None``.
        """
        return self.students_can_create_groups and (
                self.students_can_not_create_groups_after is None or
                self.students_can_not_create_groups_after > timezone.now())

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
                - If devilryrole is ``"periodadmin"``, and the assignment is anonymous, we raise ValueError.
                  This is because it is a bug for periodadmins to get access to any anonymous assignments.
                - If devilryrole is ``"subjectadmin"``, candidates need to be
                  anonymized if the assignment is anonymized with ``anonymizationmode="fully_anonymous"``.
                - If devilryrole is ``"departmentadmin"``, candidates do not need to be anonymized even
                  if the assignment is anonymous.

        Raises:
            ValueError: If the assignment is anonymous and ``devilryrole == "periodadmin"`` (explained above).

        Returns:
            bool: ``True`` if the candidates must be anonymized for the given role.
        """
        if devilryrole == 'student':
            return False
        elif devilryrole == 'examiner':
            return self.is_anonymous
        elif devilryrole == 'periodadmin':
            if self.is_anonymous:
                raise ValueError('It is illegal for periodadmins to have access to anonymous assignments.')
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
                - If devilryrole is ``"periodadmin"``, and the assignment is anonymous, we raise ValueError.
                  This is because it is a bug for periodadmins to get access to any anonymous assignments.
                - If devilryrole is ``"subjectadmin"``, examiners need to be
                  anonymized if the assignment is anonymized with ``anonymizationmode="fully_anonymous"``.
        Raises:
            ValueError: If the assignment is anonymous and ``devilryrole == "periodadmin"`` (explained above).

        Returns:
            bool: ``True`` if the examiners must be anonymized for the given role.
        """
        if devilryrole == 'student':
            return self.is_anonymous
        elif devilryrole == 'examiner':
            return False
        elif devilryrole == 'periodadmin':
            if self.is_anonymous:
                raise ValueError('It is illegal for periodadmins to have access to anonymous assignments.')
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
        Get the :class:`~devilry.apps.core.models.PointToGradeMap` for this assignment,
        or ``None`` if there is no PointToGradeMap for this assignment.
        """
        if not hasattr(self, 'prefetched_point_to_grade_map'):
            raise AttributeError('get_point_to_grade_map() requires '
                                 'AssignmentQuerySet.prefetch_point_to_grade_map().')
        return self.prefetched_point_to_grade_map

    def get_points_to_grade_map_as_cached_dict(self):
        """
        Uses :meth:`.get_point_to_grade_map` to get the grade to points map
        object, then transforms it into an OrderedDict using
        :meth:`devilry.apps.core.models.PointToGradeMap.as_flat_dict`.

        The results are cached on this Assignment object, so multiple
        calls to this method on an Assignment object does not require any
        extra performance cost.
        """
        if not hasattr(self, '_points_to_grade_map_as_cached_dict'):
            self._points_to_grade_map_as_cached_dict = self.get_point_to_grade_map() \
                .as_flat_dict()
        return self._points_to_grade_map_as_cached_dict

    def points_is_passing_grade(self, points):
        """
        Checks if the given points represents a passing grade.
        """
        return points >= self.passing_grade_min_points

    def points_to_grade(self, points):
        """
        Convert the given points into a grade.

        WARNING: This will not work if :meth:`.has_valid_grading_setup` is not ``True``.
        """
        if self.points_to_grade_mapper == self.POINTS_TO_GRADE_MAPPER_PASSED_FAILED:
            if self.points_is_passing_grade(points=points):
                return pgettext_lazy(
                    'assignment grade passed-or-failed',
                    'passed')
            else:
                return pgettext_lazy(
                    'assignment grade passed-or-failed',
                    'failed')
        elif self.points_to_grade_mapper == self.POINTS_TO_GRADE_MAPPER_RAW_POINTS:
            return '{}/{}'.format(points, self.max_points)
        elif self.points_to_grade_mapper == self.POINTS_TO_GRADE_MAPPER_CUSTOM_TABLE:
            return self.get_points_to_grade_map_as_cached_dict()[points]
        else:
            raise ValueError(
                'Assignment with id=#{} has invalid value '
                'for points_to_grade_mapper: {}'.format(
                    self.id, self.points_to_grade_mapper))

    @classmethod
    def q_published(cls, old=True, active=True):
        warnings.warn("deprecated", DeprecationWarning)
        now = timezone.now()
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
    def q_is_examiner(cls, user_obj):
        warnings.warn("deprecated", DeprecationWarning)
        return Q(assignmentgroups__examiners__user=user_obj)

    def _clean_first_deadline(self, errors):
        # NOTE: We want this so a unique deadline is a deadline which matches with second-specition.
        self.first_deadline = self.first_deadline.replace(second=59, microsecond=0)

        if self.first_deadline > self.parentnode.end_time or self.first_deadline < self.parentnode.start_time:
            errors['first_deadline'] = gettext_lazy("First deadline must be within %(periodname)s, "
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
                errors['publishing_time'] = gettext_lazy("Publishing time must be within %(periodname)s, "
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
            errors['passing_grade_min_points'] = gettext_lazy('The minumum number of points required to pass must be less than '
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
        warnings.warn("deprecated", DeprecationWarning)
        from .delivery import Delivery
        return Delivery.objects.filter(deadline__assignment_group__parentnode=self).count() == 0

    def is_active(self):
        """
        Returns ``True`` if this assignment is published, and the period has not ended yet.
        """
        warnings.warn("deprecated", DeprecationWarning)
        now = timezone.now()
        return self.publishing_time < now and self.parentnode.end_time > now

    def deadline_handling_is_hard(self):
        return self.deadline_handling == self.DEADLINEHANDLING_HARD

    def get_groups_with_passing_grade(self, sourceassignment):
        """
        Get :class:`devilry.apps.core.models.assignment_group.AssignmentGroup`s for the ``sourceassignment``
        where the last :class:`.devilry.devilry_group.models.FeedbackSet` has a passing grade.

        Args:
            sourceassignment: A :obj:`.Assignment` to copy `groups` from.

        Returns
            QuerySet: A :class:`devilry.apps.core.models.assignment_group.AssignmentGroup` queryset.
        """
        return sourceassignment.assignmentgroups \
            .filter(parentnode_id=sourceassignment.id) \
            .select_related('cached_data') \
            .filter(
            cached_data__last_published_feedbackset=models.F('cached_data__last_feedbackset'),
            cached_data__last_published_feedbackset__grading_points__gte=sourceassignment.passing_grade_min_points)

    def copy_groups_from_another_assignment(self, sourceassignment, passing_grade_only=False):
        """
        Copy all AssignmentGroup objects from another assignment.

        Copies:

        - The name of the group.
        """
        from devilry.apps.core.models import AssignmentGroup
        from devilry.apps.core.models import Candidate
        from devilry.apps.core.models import Examiner

        if self.assignmentgroups.exists():
            raise AssignmentHasGroupsError(gettext_lazy('The assignment has students. You can not '
                                             'copy use this on assignments with students.'))

        # Step1: Bulk create the groups with no candidates or examiners, but set copied_from.
        groups = []
        if not passing_grade_only:
            assignment_group_queryset = sourceassignment.assignmentgroups.all()
        else:
            assignment_group_queryset = self.get_groups_with_passing_grade(
                sourceassignment=sourceassignment)
        for othergroup in assignment_group_queryset:
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
                    relatedexaminer_id=otherexaminer.relatedexaminer_id
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
            raise AssignmentHasGroupsError(gettext_lazy('The assignment has students. You can not '
                                             'copy use this on assignments with students.'))

        # We iterate over relatedstudents twice, so we
        # use this to avoid multiple queries
        relatedstudents = list(self.period.relatedstudent_set.filter(active=True))

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

    def __prefetch_relatedstudents_with_candidates(self):
        from devilry.apps.core.models import Candidate
        return RelatedStudent.objects \
            .select_related('user') \
            .prefetch_related(
            models.Prefetch('candidate_set',
                            queryset=Candidate.objects.select_related('assignment_group')))

    def setup_examiners_by_relateduser_syncsystem_tags(self):
        from devilry.apps.core.models import Candidate
        from devilry.apps.core.models import Examiner
        from . import period_tag
        period = self.period

        # We use this to avoid adding examiners to groups they are already on
        # We could have used an exclude query, but this is more efficient because
        # it only requires one query.
        groupid_to_examineruserid_map = dict(Examiner.objects.filter(
            assignmentgroup__parentnode=self).values_list('assignmentgroup_id', 'relatedexaminer__user_id'))

        examinerobjects = []
        for periodtag in period_tag.PeriodTag.objects.filter(period=period):
            relatedstudentids = [relatedstudent.id for relatedstudent in periodtag.relatedstudents.all()]

            if relatedstudentids:
                candidate_queryset = Candidate.objects \
                    .filter(assignment_group__parentnode=self, relatedstudent_id__in=relatedstudentids) \
                    .select_related('assignment_group', 'relatedstudent', 'relatedstudent__user') \
                    .distinct()
                for relatedexaminer in periodtag.relatedexaminers.all().select_related('user'):
                    examineruser = relatedexaminer.user
                    groupids = set()
                    for candidate in candidate_queryset:
                        if groupid_to_examineruserid_map.get(candidate.assignment_group_id, None) != examineruser.id:
                            groupids.add(candidate.assignment_group_id)
                    examinerobjects.extend([Examiner(
                        assignmentgroup_id=groupid,
                        relatedexaminer=relatedexaminer) for groupid in groupids])
        if examinerobjects:
            Examiner.objects.bulk_create(examinerobjects)

    def __str__(self):
        return self.get_path()
