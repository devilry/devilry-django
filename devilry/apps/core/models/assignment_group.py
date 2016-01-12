import warnings
from datetime import datetime

from django.db.models import Q
from django.db import models
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from ievv_opensource.ievv_batchframework.models import BatchOperation

from .node import Node
from .abstract_is_admin import AbstractIsAdmin
from .abstract_is_examiner import AbstractIsExaminer
from .assignment import Assignment
from model_utils import Etag
import deliverytypes


class GroupPopValueError(ValueError):
    """
    Base class for exceptions raised by meth:`AssignmentGroup.pop_candidate`.
    """


class GroupPopToFewCandiatesError(GroupPopValueError):
    """
    Raised when meth:`AssignmentGroup.pop_candidate` is called on a group with
    1 or less candidates.
    """


class GroupPopNotCandiateError(GroupPopValueError):
    """
    Raised when meth:`AssignmentGroup.pop_candidate` is called with a candidate
    that is not on the group.
    """


class AssignmentGroupQuerySet(models.query.QuerySet):
    """
    Returns a queryset with all AssignmentGroups where the given ``user`` is examiner.

    WARNING: You should normally not use this directly because it gives the
    examiner information from expired periods (which in most cases are not necessary
    to get). Use :meth:`.active` instead.
    """

    def annotate_with_last_deadline_pk(self):
        """
        See :meth:`.AssignmentGroupManager.annotate_with_last_deadline_pk`.
        """
        return self.extra(
            select={
                'last_deadline_pk': """
                    SELECT core_deadline.id
                    FROM core_deadline
                    WHERE core_deadline.assignment_group_id = core_assignmentgroup.id
                    ORDER BY core_deadline.deadline DESC
                    LIMIT 1
                """
            },
        )

    def annotate_with_last_deadline_datetime(self):
        """
        See :meth:`.AssignmentGroupManager.annotate_with_last_deadline_datetime`.
        """
        return self.extra(
            select={
                'last_deadline_datetime': """
                    SELECT core_deadline.deadline
                    FROM core_deadline
                    WHERE core_deadline.assignment_group_id = core_assignmentgroup.id
                    ORDER BY core_deadline.deadline DESC
                    LIMIT 1
                """
            },
        )

    def annotate_with_last_delivery_id(self):
        """
        See :meth:`.AssignmentGroupManager.annotate_with_last_delivery_id`.
        """
        return self.extra(
            select={
                'last_delivery_id': """
                    SELECT core_delivery.id
                    FROM core_delivery
                    INNER JOIN core_deadline ON core_deadline.id = core_delivery.deadline_id
                    WHERE core_deadline.assignment_group_id = core_assignmentgroup.id
                    ORDER BY core_delivery.time_of_delivery DESC
                    LIMIT 1
                """
            },
        )

    def annotate_with_last_delivery_time_of_delivery(self):
        """
        See :meth:`.AssignmentGroupManager.annotate_with_last_delivery_id`.
        """
        return self.extra(
            select={
                'last_delivery_time_of_delivery': """
                    SELECT core_delivery.time_of_delivery
                    FROM core_delivery
                    INNER JOIN core_deadline ON core_deadline.id = core_delivery.deadline_id
                    WHERE core_deadline.assignment_group_id = core_assignmentgroup.id
                    ORDER BY core_delivery.time_of_delivery DESC
                    LIMIT 1
                """
            },
        )

    def annotate_with_number_of_deliveries(self):
        """
        See :meth:`.AssignmentGroupManager.annotate_with_number_of_deliveries`.
        """
        return self.annotate(number_of_deliveries=models.Count('deadlines__deliveries'))

    def exclude_groups_with_deliveries(self):
        """
        See :meth:`.AssignmentGroupManager.exclude_groups_with_deliveries`.
        """
        return self\
            .annotate(deliverycount_for_no_deliveries_exclude=models.Count('deadlines__deliveries'))\
            .filter(deliverycount_for_no_deliveries_exclude=0)

    def filter_is_examiner(self, user):
        warnings.warn('AssignmentGroupQuerySet.filter_is_examiner is deprecated in 3.0 - '
                      'use filter_user_is_examiner', DeprecationWarning)
        return self.filter(examiners__user=user).distinct()

    def filter_is_candidate(self, user):
        warnings.warn('AssignmentGroupQuerySet.filter_is_candidate is deprecated in 3.0 - '
                      'use filter_user_is_candidate', DeprecationWarning)
        return self.filter(candidates__student=user).distinct()

    def filter_user_is_examiner(self, user):
        """
        Filter all :class:`.AssignmentGroup` objects where the given
        user is examiner.

        Args:
            user: A :class:`devilry.devilry_account.models.User` object.
        """
        return self.filter(examiners__relatedexaminer__user=user).distinct()

    def filter_user_is_candidate(self, user):
        """
        Filter all :class:`.AssignmentGroup` objects where the given
        user is candidate.

        Args:
            user: A :class:`devilry.devilry_account.models.User` object.
        """
        return self.filter(candidates__relatedstudent__user=user).distinct()

    def filter_is_published(self):
        return self.filter(parentnode__publishing_time__lt=datetime.now())

    def filter_is_active(self):
        now = datetime.now()
        return self.filter_is_published().filter(
            parentnode__parentnode__start_time__lt=now,
            parentnode__parentnode__end_time__gt=now)

    def filter_examiner_has_access(self, user):
        return self.filter_is_active().filter_is_examiner(user)

    def filter_student_has_access(self, user):
        return self.filter_is_published().filter_is_candidate(user)

    def filter_by_status(self, status):
        return self.filter(delivery_status=status)

    def filter_waiting_for_feedback(self):
        now = datetime.now()
        return self.filter(
            Q(parentnode__delivery_types=deliverytypes.NON_ELECTRONIC,
              delivery_status="waiting-for-something") |
            Q(parentnode__delivery_types=deliverytypes.ELECTRONIC,
              delivery_status="waiting-for-something",
              last_deadline__deadline__lte=now))

    def filter_waiting_for_deliveries(self):
        now = datetime.now()
        return self.filter(
            parentnode__delivery_types=deliverytypes.ELECTRONIC,
            delivery_status="waiting-for-something",
            last_deadline__deadline__gt=now)

    def filter_can_add_deliveries(self):
        now = datetime.now()
        return self\
            .filter(parentnode__delivery_types=deliverytypes.ELECTRONIC,
                    delivery_status="waiting-for-something")\
            .extra(
                where=[
                    """
                    core_assignment.deadline_handling = %s
                    OR
                    (SELECT core_deadline.deadline
                     FROM core_deadline
                     WHERE core_deadline.assignment_group_id = core_assignmentgroup.id
                     ORDER BY core_deadline.deadline DESC
                     LIMIT 1) > %s
                    """
                ],
                params=[
                    Assignment.DEADLINEHANDLING_SOFT,
                    now
                ]
            )

    def close_groups(self):
        return self.update(
            is_open=False,
            delivery_status='closed-without-feedback'
        )

    def add_nonelectronic_delivery(self):
        from devilry.apps.core.models import Delivery
        for group in self.all():
            deadline = group.last_deadline
            delivery = Delivery(
                deadline=deadline,
                delivery_type=deliverytypes.NON_ELECTRONIC,
                time_of_delivery=datetime.now())
            delivery.set_number()
            delivery.full_clean()
            delivery.save()

    def filter_has_passing_grade(self, assignment):
        """
        Filter only :class:`.AssignmentGroup` objects within the given
        assignment that has a passing grade.

        That means that this filters out all AssignmentGroups where
        the latest published :class:`devilry.devilry_group.models.FeedbackSet`
        has less :obj:`devilry.devilry_group.models.FeedbackSet.grading_points`
        than the ``passing_grade_min_points`` for the assignment.

        This method performs ``filter(parentnode=assignment)``
        in addition to the query that checks the feedbacksets.

        Args:
            assignment: A :class:`devilry.apps.core.models.assignment.Assignment` object.
        """
        return self.filter(parentnode=assignment)\
            .extra(
                where=[
                    """
                    (
                        SELECT devilry_group_feedbackset.grading_points
                        FROM devilry_group_feedbackset
                        WHERE
                            devilry_group_feedbackset.group_id = core_assignmentgroup.id
                            AND
                            devilry_group_feedbackset.grading_published_datetime IS NOT NULL
                        ORDER BY devilry_group_feedbackset.grading_published_datetime DESC
                        LIMIT 1
                    ) >= %s
                    """
                ],
                params=[
                    assignment.passing_grade_min_points
                ]
            )

    def annotate_with_number_of_groupcomments(self):
        """
        Annotate the queryset with ``number_of_groupcomments`` -
        the number of :class:`devilry.devilry_group.models.GroupComment`
        within each AssignmentGroup.
        """
        return self.annotate(
            number_of_groupcomments=models.Count(
                'feedbackset__groupcomment'
            )
        )

    def annotate_with_number_of_imageannotationcomments(self):
        """
        Annotate the queryset with ``number_of_imageannotationcomments`` -
        the number of :class:`devilry.devilry_group.models.ImageAnnotationComment`
        within each AssignmentGroup.
        """
        return self.annotate(
            number_of_imageannotationcomments=models.Count(
                'feedbackset__imageannotationcomment'
            )
        )

    def annotate_with_number_of_published_feedbacksets(self):
        """
        Annotate the queryset with ``number_of_published_feedbacksets`` -
        the number of :class:`devilry.devilry_group.models.FeedbackSet` with
        :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`
        set to a non-null value within each AssignmentGroup.
        """
        return self.annotate(
            number_of_published_feedbacksets=models.Count(
                models.Case(
                    # When grading_published_datetime, count that as 1 in the Count.
                    models.When(feedbackset__grading_published_datetime__isnull=False,
                                then=1)
                )
            )
        )

    def filter_with_published_feedback_or_comments(self):
        """
        Filter only :class:`.AssignmentGroup` objects containing
        :class:`devilry.devilry_group.models.FeedbackSet` with
        :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`
        or any comments.
        """
        return self.annotate_with_number_of_groupcomments()\
            .annotate_with_number_of_imageannotationcomments()\
            .annotate_with_number_of_published_feedbacksets()\
            .filter(
                models.Q(number_of_published_feedbacksets__gt=0) |
                models.Q(number_of_imageannotationcomments__gt=0) |
                models.Q(number_of_groupcomments__gt=0)
            )


class AssignmentGroupManager(models.Manager):
    def get_queryset(self):
        return AssignmentGroupQuerySet(self.model, using=self._db)

    def filter(self, *args, **kwargs):
        return self.get_queryset().filter(*args, **kwargs)

    def annotate_with_last_deadline_pk(self):
        """
        Annotate the queryset with the datetime of the last deadline stored
        as the ``last_deadline_id`` attribute.
        """
        return self.get_queryset().annotate_with_last_deadline_pk()

    def annotate_with_last_deadline_datetime(self):
        """
        Annotate the queryset with the datetime of the last deadline stored
        as the ``last_deadline_datetime`` attribute.
        """
        return self.get_queryset().annotate_with_last_deadline_datetime()

    def annotate_with_last_delivery_time_of_delivery(self):
        """
        Annotate the queryset with the time of delivery of the last delivery stored
        as the ``last_delivery_time_of_delivery`` attribute.
        """
        return self.get_queryset().annotate_with_last_delivery_time_of_delivery()

    def annotate_with_last_delivery_id(self):
        """
        Annotate the queryset with the ID of the last delivery stored
        as the ``last_delivery_id`` attribute.
        """
        return self.get_queryset().annotate_with_last_delivery_id()

    def annotate_with_number_of_deliveries(self):
        """
        Annotate the queryset with the number of deliveries
        as the ``number_of_deliveries`` attribute.
        """
        return self.get_queryset().annotate_with_number_of_deliveries()

    def exclude_groups_with_deliveries(self):
        """
        Filter out all groups with deliveries.

        Example::

            groups_with_no_deliveries = AssignmentGroup.objects.exclude_groups_with_deliveries()
        """
        return self.get_queryset().exclude_groups_with_deliveries()

    def filter_is_examiner(self, user):
        return self.get_queryset().filter_is_examiner(user)

    def filter_is_candidate(self, user):
        return self.get_queryset().filter_is_candidate(user)

    def filter_user_is_examiner(self, user):
        """
        Returns a queryset with all AssignmentGroups where the given ``user`` is examiner.

        See :meth:`.AssignmentGroupQuerySet.filter_user_is_examiner`.

        WARNING: You should normally not use this directly because it gives the
        examiner information from expired periods (which they are not supposed
        to get). Use :meth:`.filter_examiner_has_access` instead.
        """
        return self.get_queryset().filter_user_is_examiner(user)

    def filter_user_is_candidate(self, user):
        """
        Returns a queryset with all AssignmentGroups where the given ``user`` is candidate.

        See :meth:`.AssignmentGroupQuerySet.filter_user_is_candidate`.

        WARNING: You should normally not use this directly because it gives the
        student information from unpublished assignments (which they are not supposed
        to get). Use :meth:`.filter_student_has_access` instead.
        """
        return self.get_queryset().filter_user_is_candidate(user)

    def filter_is_published(self):
        """
        Returns a queryset with all AssignmentGroups on published Assignments.
        """
        return self.get_queryset().filter_is_published()

    def filter_is_active(self):
        """
        Returns a queryset with all AssignmentGroups on active Assignments.
        """
        return self.get_queryset().filter_is_active()

    def filter_examiner_has_access(self, user):
        """
        Returns a queryset with all AssignmentGroups on active Assignments
        where the given ``user`` is examiner.

        NOTE: This returns all groups that the given ``user`` has examiner-rights for.
        """
        return self.get_queryset().filter_examiner_has_access(user)

    def filter_student_has_access(self, user):
        """
        Returns a queryset with all AssignmentGroups on published Assignments
        where the given ``user`` is a candidate.

        NOTE: This returns all groups that the given ``user`` has student-rights for.
        """
        return self.get_queryset().filter_student_has_access(user)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def filter_waiting_for_feedback(self):
        return self.get_queryset().filter_waiting_for_feedback()

    def filter_waiting_for_deliveries(self):
        return self.get_queryset().filter_waiting_for_deliveries()

    def filter_can_add_deliveries(self):
        return self.get_queryset().filter_can_add_deliveries()

    def close_groups(self):
        """
        Performs an efficient update of all the groups in the queryset
        setting ``is_open=False`` and ``delivery_status="closed-without-feedback"``.
        """
        return self.get_queryset().close_groups()

    def add_nonelectronic_delivery(self):
        """
        Add non-electronic delivery to all the groups in the queryset.

        Assumes that all the groups has ``last_deadline`` set.
        """
        return self.get_queryset().add_nonelectronic_delivery()

    def __bulk_create_groups(self, assignment, batchoperation, relatedstudents):
        groups = []
        for relatedstudent in relatedstudents:
            group = AssignmentGroup(
                batchoperation=batchoperation,
                parentnode=assignment)
            groups.append(group)
        AssignmentGroup.objects.bulk_create(groups)
        return AssignmentGroup.objects.filter(batchoperation=batchoperation)

    def __bulk_create_candidates(self, group_list, relatedstudents):
        from devilry.apps.core.models import Candidate
        candidates = []
        for group, relatedstudent in zip(group_list, relatedstudents):
            candidate = Candidate(
                student=relatedstudent.user,
                relatedstudent=relatedstudent,
                assignment_group=group)
            candidates.append(candidate)
        Candidate.objects.bulk_create(candidates)

    def __bulk_create_feedbacksets(self, group_list, created_by_user):
        from devilry.devilry_group.models import FeedbackSet
        feedbacksets = []
        for group in group_list:
            feedbackset = FeedbackSet(
                group=group,
                created_by=created_by_user)
            feedbacksets.append(feedbackset)
        FeedbackSet.objects.bulk_create(feedbacksets)

    def bulk_create_groups(self, created_by_user, assignment, relatedstudents):
        """
        Bulk create :class:`~.AssignmentGroup` objects, one for each
        :class:`~devilry.apps.core.models.relateduser.RelatedStudent` in
        ``relatedstudents``.

        The groups are created with:

        - one :class:`devilry.apps.core.models.candidate.Candidate` (so each RelatedStudent
          is added a Candidate on a group).
        - one :class:`devilry.devilry_group.models.FeedbackSet`.

        Args:
            created_by_user: The user that created the groups.
            assignment: The :class:`:class:`~devilry.apps.core.models.assignment.Assignment` to add
                the groups to.
            relatedstudents: Iterable of :class:`~devilry.apps.core.models.relateduser.RelatedStudent`
                objects. Should not be a queryset, because this method loops over the iterable
                multiple times. So if you have a queryset of RelatedStudents, use
                ``bulk_create_groups(relatedstudents=list(relatedstudent_queryset))``.

        Returns:
            django.db.models.query.QuerySet: A queryset with the created groups.
        """
        batchoperation = BatchOperation.objects.create_syncronous(
            context_object=assignment,
            operationtype='create-groups-with-candidate-and-feedbackset')
        group_queryset = self.__bulk_create_groups(assignment=assignment,
                                                   batchoperation=batchoperation,
                                                   relatedstudents=relatedstudents)
        # We iterate over the groups multiple times, so we do this to avoid multiple queries
        group_list = list(group_queryset)

        self.__bulk_create_candidates(group_list=group_list,
                                      relatedstudents=relatedstudents)
        self.__bulk_create_feedbacksets(created_by_user=created_by_user,
                                        group_list=group_list)
        batchoperation.finish()
        return group_queryset

    def filter_has_passing_grade(self, assignment):
        """
        See :meth:`.AssignmentGroupQuerySet.filter_has_passing_grade`.
        """
        return self.get_queryset().filter_has_passing_grade(assignment=assignment)

    def filter_with_published_feedback_or_comments(self):
        """
        See :meth:`.AssignmentGroupQuerySet.filter_with_published_feedback_or_comments`.
        """
        return self.get_queryset().filter_with_published_feedback_or_comments()

    def annotate_with_number_of_groupcomments(self):
        """
        See :meth:`.AssignmentGroupQuerySet.annotate_with_number_of_groupcomments`.
        """
        return self.get_queryset().annotate_with_number_of_groupcomments()

    def annotate_with_number_of_published_feedbacksets(self):
        """
        See :meth:`.AssignmentGroupQuerySet.annotate_with_number_of_published_feedbacksets`.
        """
        return self.get_queryset().annotate_with_number_of_published_feedbacksets()

    def annotate_with_number_of_imageannotationcomments(self):
        """
        See :meth:`.AssignmentGroupQuerySet.annotate_with_number_of_imageannotationcomments`.
        """
        return self.get_queryset().annotate_with_number_of_imageannotationcomments()


# TODO: Constraint: cannot be examiner and student on the same assignmentgroup as an option.
class AssignmentGroup(models.Model, AbstractIsAdmin, AbstractIsExaminer, Etag):
    """
    Represents a student or a group of students.

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always an `Assignment`_.

    .. attribute:: name

        An optional name for the group.

    .. attribute:: candidates

        A django ``RelatedManager`` that holds the :class:`candidates <devilry.apps.core.models.Candidate>`
        on this group.

    .. attribute:: examiners

        A django.db.models.ManyToManyField_ that holds the examiner(s) that are
        to correct and grade the assignment.

    .. attribute:: is_open

        A django.db.models.BooleanField_ that tells you if the group can add
        deliveries or not.

    .. attribute:: deadlines

        A django ``RelatedManager`` that holds the :class:`deadlines <devilry.apps.core.models.Deadline>`
        on this group.

    .. attribute:: tags

        A django ``RelatedManager`` that holds the :class:`tags <devilry.apps.core.models.AssignmentGroupTag>`
        on this group.

    .. attribute:: feedback

       The last `StaticFeedback`_ (by save timestamp) on this assignmentgroup.


    .. attribute:: last_deadline

       The last :class:`devilry.apps.core.models.Deadline` for this assignmentgroup.

    .. attribute:: etag

       A DateTimeField containing the etag for this object.

    .. attribute:: delivery_status

       A CharField containing the status of the group.
       Valid status values:

           * "no-deadlines"
           * "corrected"
           * "closed-without-feedback"
           * "waiting-for-something"
    """

    objects = AssignmentGroupManager()

    parentnode = models.ForeignKey(Assignment, related_name='assignmentgroups')
    name = models.CharField(
        max_length=30, blank=True, null=False, default='',
        help_text='An optional name for the group. Typically used a project '
                  'name on project assignments.')
    is_open = models.BooleanField(
        blank=True, default=True,
        help_text='If this is checked, the group can add deliveries.')
    feedback = models.OneToOneField("StaticFeedback", blank=True, null=True,
                                    on_delete=models.SET_NULL)
    last_deadline = models.OneToOneField(
        "Deadline", blank=True, null=True,
        related_name='last_deadline_for_group', on_delete=models.SET_NULL)
    etag = models.DateTimeField(auto_now_add=True)
    delivery_status = models.CharField(
        max_length=30, blank=True, null=True,
        help_text='The delivery_status of a group',
        choices=(
            ("no-deadlines", _("No deadlines")),
            ("corrected", _("Corrected")),
            ("closed-without-feedback", _("Closed without feedback")),
            ("waiting-for-something", _("Waiting for something")),
        ))

    #: Foreignkey to :class:`ievv_opensource.ievv_batchframework.models.BatchOperation`.
    #: When we perform batch operations on the assignmentgroup, this is used to reference
    #: the operation. Batch operations include bulk-create - we use the BatchOperation
    #: object to enable us to recursively batch create AssignmentGroup,
    #: Candidate and FeedbackSet in a very efficient batch operation with
    #: a fixed set of database queries.
    batchoperation = models.ForeignKey(
        to=BatchOperation,
        null=True, blank=True,
        on_delete=models.SET_NULL)

    #: If this group was copied from another group, this will be set.
    #: This can safely be set to ``None`` at any time since it is only
    #: used to make it possible to bulk copy huge amounts of groups
    #: efficiently.
    copied_from = models.ForeignKey('self',
                                    on_delete=models.SET_NULL,
                                    blank=True, null=True)

    #: The time when this group was created.
    created_datetime = models.DateTimeField(null=False, blank=True,
                                            default=timezone.now)

    class Meta:
        app_label = 'core'
        ordering = ['id']

    def save(self, *args, **kwargs):
        """
        :param update_delivery_status:
            Update the ``delivery_status``? This is a somewhat expensive
            operation, so we provide the option to avoid it if needed.
            Defaults to ``True``.
        :param autocreate_first_deadline_for_nonelectronic:
            Autocreate the first deadline if non-electronic assignment?
            Defaults to ``True``.
        """
        autocreate_first_deadline_for_nonelectronic = kwargs.pop('autocreate_first_deadline_for_nonelectronic', True)
        create_dummy_deadline = False
        if autocreate_first_deadline_for_nonelectronic \
                and self.id is None \
                and self.parentnode.delivery_types == deliverytypes.NON_ELECTRONIC:
            create_dummy_deadline = True
        if kwargs.pop('update_delivery_status', True):
            self._set_delivery_status()
        super(AssignmentGroup, self).save(*args, **kwargs)
        if create_dummy_deadline:
            self.deadlines.create(deadline=self.parentnode.parentnode.end_time)

    @classmethod
    def q_is_admin(cls, user_obj):
        return Q(parentnode__admins=user_obj) | \
            Q(parentnode__parentnode__admins=user_obj) | \
            Q(parentnode__parentnode__parentnode__admins=user_obj) | \
            Q(parentnode__parentnode__parentnode__parentnode__pk__in=Node._get_nodepks_where_isadmin(user_obj))

    @classmethod
    def q_is_candidate(cls, user_obj):
        """
        Returns a django.models.Q object matching AssignmentGroups where
        the given student is candidate.
        """
        return Q(candidates__student=user_obj)

    @classmethod
    def where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all AssignmentGroups where the
        given user is student.

        :param user_obj: A User object.
        :rtype: QuerySet
        """
        return AssignmentGroup.objects.filter(cls.q_is_candidate(user_obj))

    @classmethod
    def published_where_is_candidate(cls, user_obj, old=True, active=True):
        """ Returns a QuerySet matching all :ref:`published
        <assignment-classifications>` assignment groups where the given user
        is student.

        :param user_obj: A User object.
        :rtype: QuerySet
        """
        return AssignmentGroup.objects.filter(
            cls.q_is_candidate(user_obj) &
            cls.q_published(old=old, active=active))

    @classmethod
    def active_where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`active
        <assignment-classifications>` assignment groups where the given user
        is student.

        :param user_obj: A User object.
        :rtype: QuerySet
        """
        return cls.published_where_is_candidate(user_obj, old=False)

    @classmethod
    def old_where_is_candidate(cls, user_obj):
        """ Returns a QuerySet matching all :ref:`old
        <assignment-classifications>` assignment groups where the given user
        is student.

        :param user_obj: A User object.
        :rtype: QuerySet
        """
        return cls.published_where_is_candidate(user_obj, active=False)

    @classmethod
    def q_published(cls, old=True, active=True):
        now = datetime.now()
        q = Q(parentnode__publishing_time__lt=now)
        if not active:
            q &= ~Q(parentnode__parentnode__end_time__gte=now)
        if not old:
            q &= ~Q(parentnode__parentnode__end_time__lt=now)
        return q

    @classmethod
    def q_is_examiner(cls, user_obj):
        return Q(examiners__user=user_obj)

    @property
    def should_ask_if_examiner_want_to_give_another_chance(self):
        """
        ``True`` if the current state of the group is such that the examiner should
        be asked if they want to give them another chance.

        ``True`` if corrected with failing grade or closed without feedback.
        """
        if self.assignment.is_electronic:
            return (self.delivery_status == "corrected" and not self.feedback.is_passing_grade) \
                or self.delivery_status == 'closed-without-feedback'
        else:
            return False

    @property
    def missing_expected_delivery(self):
        """
        Return ``True`` if the group has no deliveries, and we are expecting
        them to have made at least one delivery on the last deadline.
        """
        from devilry.apps.core.models import Delivery
        from devilry.apps.core.models import Deadline
        if self.assignment.is_electronic and self.get_status() == "waiting-for-feedback":
            return not Delivery.objects.filter(
                deadline__assignment_group=self,
                deadline=Deadline.objects.filter(assignment_group=self).order_by('-deadline')[0]
            ).exists()
        return False

    @property
    def subject(self):
        """
        Shortcut for ``parentnode.parentnode.parentnode``.
        """
        return self.parentnode.parentnode.parentnode

    @property
    def period(self):
        """
        Shortcut for ``parentnode.parentnode``.
        """
        return self.parentnode.parentnode

    @property
    def assignment(self):
        """
        Alias for :obj:`.parentnode`.
        """
        return self.parentnode

    def get_anonymous_displayname(self, assignment=None):
        """
        Get the anonymous displayname for this group.

        Args:
            assignment: An optional :class:`devilry.apps.core.models.assignment.Assignment`.
                if this is provided, we use this instead of looking up
                ``parentnode``. This is essential for views
                that list many groups since it avoid extra database lookups.
        """
        if assignment is None:
            assignment = self.assignment

        candidateids = []
        for candidate in self.candidates.all():
            candidateids.append(candidate.get_anonymous_name(assignment=assignment))
        if candidateids:
            return u', '.join(candidateids)
        else:
            return pgettext_lazy('core assignmentgroup',
                                 'no students in group')

    def __get_no_candidates_nonanonymous_displayname(self):
        return pgettext_lazy('core assignmentgroup',
                             'group#%(groupid)s - no students in group') % {
            'groupid': self.id
        }

    @property
    def short_displayname(self):
        """
        A short displayname for the group. If the assignment is anonymous,
        we list the candidate IDs. If the group has a name, the name is used,
        else we fall back to a comma separated list of usernames. If the group has no name and no
        students, we use the ID.

        .. seealso:: https://github.com/devilry/devilry-django/issues/498
        """
        assignment = self.assignment
        if assignment.is_anonymous:
            return self.get_anonymous_displayname()
        else:
            candidates = self.candidates.all()
            names = [candidate.relatedstudent.user.shortname for candidate in candidates]
            out = u', '.join(names)
            if out:
                if self.name:
                    return self.name
                else:
                    return out
            else:
                return self.__get_no_candidates_nonanonymous_displayname()

    @property
    def long_displayname(self):
        """
        A long displayname for the group. If the assignment is anonymous,
        we list the candidate IDs.

        If the assignment is not anonymous, we use a comma separated list of
        the displaynames (full names with fallback to shortname) of the
        students. If the group has a name, we use the groupname with the names
        of the students in parenthesis.

        .. seealso:: https://github.com/devilry/devilry-django/issues/499
        """
        assignment = self.assignment
        if assignment.is_anonymous:
            out = self.get_anonymous_displayname()
        else:
            candidates = self.candidates.all()
            names = [candidate.relatedstudent.user.get_full_name() for candidate in candidates]
            out = u', '.join(names)
            if not out:
                out = self.__get_no_candidates_nonanonymous_displayname()
            if self.name:
                out = u'{} ({})'.format(self.name, out)
        return out

    def __unicode__(self):
        return u'{} - {}'.format(self.short_displayname, self.parentnode.get_path())

    def get_examiners(self, separator=u', '):
        """
        Get a string contaning the shortname of all examiners in the group separated by
        comma (``','``).

        :param separator: The unicode string used to separate candidates. Defaults to ``u', '``.
        """
        warnings.warn("deprecated", DeprecationWarning)
        examiners = [examiner.user.shortname for examiner in self.examiners.select_related('user')]
        examiners.sort()
        return separator.join(examiners)

    def is_admin(self, user_obj):
        warnings.warn("deprecated", DeprecationWarning)
        return self.parentnode.is_admin(user_obj)

    def is_candidate(self, user_obj):
        warnings.warn("deprecated", DeprecationWarning)
        return self.candidates.filter(student=user_obj).count() > 0

    def is_examiner(self, user_obj):
        """ Return True if user is examiner on this assignment group """
        warnings.warn("deprecated", DeprecationWarning)
        return self.examiners.filter(user__id=user_obj.pk).count() > 0

    def can_delete(self, user_obj):
        """
        Check if the given user is permitted to delete this AssignmentGroup. A user is
        permitted to delete an object if the user is superadmin, or if the user
        is admin on the assignment (uses :meth:`.is_admin`). Only superusers
        are allowed to delete AssignmentGroups where :meth:`.AssignmentGroup.is_empty` returns ``False``.

        .. note::
            This method can also be used to check if candidates can be
            removed from the group.

        :return: ``True`` if the user is permitted to delete this object.
        """
        if self.id is None:
            return False
        if user_obj.is_superuser:
            return True
        if self.parentnode is not None and self.is_empty():
            return self.parentnode.is_admin(user_obj)
        else:
            return False

    def is_empty(self):
        """
        Returns ``True`` if this AssignmentGroup does not contain any deliveries.
        """
        from .delivery import Delivery
        return Delivery.objects.filter(deadline__assignment_group=self).count() == 0

    def get_active_deadline(self):
        """ Get the active :class:`Deadline`.

        This is always the last deadline on this group.

        :return:
            The latest deadline or ``None``.
        """
        return self.deadlines.all().order_by('-deadline').first()

    def can_save(self, user_obj):
        """ Check if the user has permission to save this AssignmentGroup. """
        if user_obj.is_superuser:
            return True
        elif self.parentnode:
            return self.parentnode.is_admin(user_obj)
        else:
            return False

    def can_add_deliveries(self):
        """ Returns true if a student can add deliveries on this assignmentgroup

        Both the assignmentgroups is_open attribute, and the periods start
        and end time is checked.
        """
        warnings.warn("deprecated", DeprecationWarning)
        return self.is_open and self.parentnode.parentnode.is_active()

    def copy_all_except_candidates(self):
        """
        .. note:: Always run this is a transaction.
        """
        groupcopy = AssignmentGroup(parentnode=self.parentnode,
                                    name=self.name,
                                    is_open=self.is_open,
                                    delivery_status=self.delivery_status)
        groupcopy.full_clean()
        groupcopy.save(update_delivery_status=False)
        for tagobj in self.tags.all():
            groupcopy.tags.create(tag=tagobj.tag)
        for examiner in self.examiners.all():
            groupcopy.examiners.create(user=examiner.user)
        for deadline in self.deadlines.all():
            deadline.copy(groupcopy)
        groupcopy._set_latest_feedback_as_active()
        groupcopy.save(update_delivery_status=False)
        return groupcopy

    def pop_candidate(self, candidate):
        """
        Make a copy of this group using ``copy_all_except_candidates``, and
        add given candidate to the copied group and remove the candidate from
        this group.

        :param candidate: A :class:`devilry.apps.core.models.Candidate` object.
            The candidate must be among the candidates on this group.

        .. note:: Always run this is a transaction.
        """
        candidates = self.candidates.all()
        if len(candidates) < 2:
            raise GroupPopToFewCandiatesError('Can not pop candidates on a group with less than 2 candidates.')
        if candidate not in candidates:
            raise GroupPopNotCandiateError('The candidate to pop must be in the original group.')

        groupcopy = self.copy_all_except_candidates()
        candidate.assignment_group = groupcopy  # Move the candidate to the new group
        candidate.full_clean()
        candidate.save()
        return groupcopy

    def recalculate_delivery_numbers(self):
        """
        Query all ``successful`` deliveries on this AssignmentGroup, ordered by
        ``time_of_delivery`` ascending, and number them with the oldest delivery
        as number 1.
        """
        from .delivery import Delivery
        qry = Delivery.objects.filter(deadline__assignment_group=self,
                                      successful=True)
        qry = qry.order_by('time_of_delivery')
        for number, delivery in enumerate(qry, 1):
            delivery.number = number
            delivery.save()

    @property
    def successful_delivery_count(self):
        warnings.warn("deprecated", DeprecationWarning)
        from .delivery import Delivery
        return Delivery.objects.filter(
            successful=True,
            deadline__assignment_group=self).count()

    def _set_delivery_status(self):
        """
        Set the ``delivery_status``. Calculated with this algorithm:

        - If open:
            - If no deadlines
                - ``no-deadlines``
            - Else:
                - ``waiting-for-something``
        - If closed:
            - If feedback:
                - ``corrected``
            - If not:
                - ``closed-without-feedback``

        .. warning:: Only sets ``delivery_status``, does not save.

        :return:
            One of ``waiting-for-deliveries``, ``waiting-for-feedback``,
            ``no-deadlines``, ``corrected`` or ``closed-without-feedback``.
        """
        if self.is_open:
            if self.deadlines.exists():
                self.delivery_status = 'waiting-for-something'
            else:
                self.delivery_status = 'no-deadlines'
        else:
            if self.feedback:
                self.delivery_status = 'corrected'
            else:
                self.delivery_status = 'closed-without-feedback'

    def _merge_examiners_into(self, target):
        target_examiners = set([e.user.id for e in target.examiners.all()])
        for examiner in self.examiners.all():
            if examiner.user.id not in target_examiners:
                examiner.assignmentgroup = target
                examiner.save()

    def _merge_candidates_into(self, target):
        target_candidates = set([e.student.id for e in target.candidates.all()])
        for candidate in self.candidates.all():
            if candidate.student.id not in target_candidates:
                candidate.assignment_group = target
                candidate.save()

    def _set_latest_feedback_as_active(self):
        from .static_feedback import StaticFeedback
        feedbacks = StaticFeedback.objects\
            .order_by('-save_timestamp')\
            .filter(delivery__deadline__assignment_group=self)[:1]
        self.feedback = None  # NOTE: Required to avoid IntegrityError caused by non-unique feedback_id
        if len(feedbacks) == 1:
            latest_feedback = feedbacks[0]
            self.feedback = latest_feedback

    def merge_into(self, target):
        """
        Merge this AssignmentGroup into the ``target`` AssignmentGroup.
        Algorithm:

            - Copy in all candidates and examiners not already on the
              AssignmentGroup.
            - Delete all copies where the original is in ``self`` or ``target``:
                - Delete all deliveries from ``target`` that are ``copy_of`` a delivery
                  ``self``.
                - Delete all deliveries from ``self`` that are ``copy_of`` a delivery in
                  ``target``.
            - Loop through all deadlines in this AssignmentGroup, and for each
              deadline:

              If the datetime and text of the deadline matches one already in
              ``target``, move the remaining deliveries into the target deadline.

              If the deadline and text does NOT match a deadline already in
              ``target``, change assignmentgroup of the deadline to the
              master group.
            - Recalculate delivery numbers of ``target`` using
              :meth:`recalculate_delivery_numbers`.
            - Run ``self.delete()``.
            - Set the latest feedback on ``target`` as the active feedback.

        .. note::
            The ``target.name`` or ``target.is_open`` is not changed.

        .. note::
            Everything except setting the latest feedback runs in a
            transaction. Setting the latest feedback does not run
            in transaction because we need to save the with ``feedback=None``,
            and then set the *new* latest feedback to avoid IntegrityError.
        """
        from .deadline import Deadline
        from .delivery import Delivery
        with transaction.atomic():
            # Unset last_deadline - if we not do this, we will get
            # ``IntegrityError: column last_deadline_id is not unique``
            # if the last deadline after the merge is self.last_deadline
            self.last_deadline = None
            self.save(update_delivery_status=False)

            # Copies
            Delivery.objects.filter(deadline__assignment_group=self,
                                    copy_of__deadline__assignment_group=target).delete()
            Delivery.objects.filter(deadline__assignment_group=target,
                                    copy_of__deadline__assignment_group=self).delete()

            # Examiners and candidates
            self._merge_examiners_into(target)
            self._merge_candidates_into(target)

            # Deadlines
            for deadline in self.deadlines.all():
                try:
                    matching_deadline = target.deadlines.get(deadline=deadline.deadline,
                                                             text=deadline.text)
                    for delivery in deadline.deliveries.all():
                        if delivery.copy_of:
                            # NOTE: If we merge 2 groups with a copy from the same third group, we
                            #       we only want one of the copies.
                            if Delivery.objects.filter(deadline__assignment_group=target,
                                                       copy_of=delivery.copy_of).exists():
                                continue
                        delivery.deadline = matching_deadline
                        delivery.save()
                except Deadline.DoesNotExist:
                    deadline.assignment_group = target
                    deadline.save()
            target.recalculate_delivery_numbers()
            self.delete()
        target._set_latest_feedback_as_active()
        target.save()

    @classmethod
    def merge_many_groups(self, sources, target):
        """
        Loop through the ``sources``-iterable, and for each ``source`` in the
        iterator, run ``source.merge_into(target)``.
        """
        for source in sources:
            source.merge_into(target)  # Source is deleted after this

    def get_status(self):
        """
        Get the status of the group. Calculated with this algorithm::

            if ``delivery_status == 'waiting-for-something'``
                if assignment.delivery_types==NON_ELECTRONIC:
                    "waiting-for-feedback"
                else
                    if before deadline
                        "waiting-for-deliveries"
                    if after deadline:
                        "waiting-for-feedback"
            else
                delivery_status
        """
        if self.delivery_status == 'waiting-for-something':
            if self.assignment.delivery_types == deliverytypes.NON_ELECTRONIC:
                return 'waiting-for-feedback'
            else:
                now = datetime.now()
                if self.last_deadline.deadline > now:
                    return 'waiting-for-deliveries'
                else:
                    return 'waiting-for-feedback'
        else:
            return self.delivery_status

    def get_all_admin_ids(self):
        warnings.warn("deprecated", DeprecationWarning)
        return self.parentnode.get_all_admin_ids()


class AssignmentGroupTag(models.Model):
    """
    An AssignmentGroup can be tagged with zero or more tags using this class.

    .. attribute:: assignment_group

        The `AssignmentGroup`_ where this groups belongs.

    .. attribute:: tag

        The tag. Max 20 characters. Can only contain a-z, A-Z, 0-9 and "_".
    """
    assignment_group = models.ForeignKey(AssignmentGroup, related_name='tags')
    tag = models.SlugField(max_length=20, help_text='A tag can contain a-z, A-Z, 0-9 and "_".')

    class Meta:
        app_label = 'core'
        ordering = ['tag']
        unique_together = ('assignment_group', 'tag')

    def __unicode__(self):
        return self.tag
