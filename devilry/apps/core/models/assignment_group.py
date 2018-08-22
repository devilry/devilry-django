import warnings

from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from ievv_opensource.ievv_batchframework.models import BatchOperation

import deliverytypes
from devilry.apps.core.models import Subject, Period
from devilry.devilry_account.models import PeriodPermissionGroup
from devilry.devilry_comment.models import Comment
from devilry.devilry_dbcache.bulk_create_queryset_mixin import BulkCreateQuerySetMixin
from model_utils import Etag
from .abstract_is_admin import AbstractIsAdmin
from .abstract_is_examiner import AbstractIsExaminer
from .assignment import Assignment


class GroupPopValueError(ValueError):
    """
    Base class for exceptions raised by meth:`AssignmentGroup.pop_candidate`.
    """


class GroupPopToFewCandidatesError(GroupPopValueError):
    """
    Raised when meth:`AssignmentGroup.pop_candidate` is called on a group with
    1 or less candidates.
    """


class GroupPopNotCandidateError(GroupPopValueError):
    """
    Raised when meth:`AssignmentGroup.pop_candidate` is called with a candidate
    that is not on the group.
    """


class AssignmentGroupQuerySet(models.QuerySet, BulkCreateQuerySetMixin):
    """
    QuerySet for :class:`.AssignmentGroup`
    """

    def annotate_with_last_deadline_pk(self):
        warnings.warn("deprecated", DeprecationWarning)
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
        warnings.warn("deprecated", DeprecationWarning)
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
        warnings.warn("deprecated", DeprecationWarning)
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
        warnings.warn("deprecated", DeprecationWarning)
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
        warnings.warn("deprecated", DeprecationWarning)
        return self.annotate(number_of_deliveries=models.Count('deadlines__deliveries'))

    def exclude_groups_with_deliveries(self):
        warnings.warn("deprecated", DeprecationWarning)
        return self\
            .annotate(deliverycount_for_no_deliveries_exclude=models.Count('deadlines__deliveries'))\
            .filter(deliverycount_for_no_deliveries_exclude=0)

    def filter_by_status(self, status):
        warnings.warn("deprecated", DeprecationWarning)
        return self.filter(delivery_status=status)

    def filter_waiting_for_feedback(self):
        warnings.warn("deprecated", DeprecationWarning)
        now = timezone.now()
        return self.filter(
            Q(parentnode__delivery_types=deliverytypes.NON_ELECTRONIC,
              delivery_status="waiting-for-something") |
            Q(parentnode__delivery_types=deliverytypes.ELECTRONIC,
              delivery_status="waiting-for-something",
              last_deadline__deadline__lte=now))

    def filter_waiting_for_deliveries(self):
        warnings.warn("deprecated", DeprecationWarning)
        now = timezone.now()
        return self.filter(
            parentnode__delivery_types=deliverytypes.ELECTRONIC,
            delivery_status="waiting-for-something",
            last_deadline__deadline__gt=now)

    def filter_can_add_deliveries(self):
        warnings.warn("deprecated", DeprecationWarning)
        now = timezone.now()
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
        warnings.warn("deprecated", DeprecationWarning)
        return self.update(
            is_open=False,
            delivery_status='closed-without-feedback'
        )

    def add_nonelectronic_delivery(self):
        warnings.warn("deprecated", DeprecationWarning)
        from devilry.apps.core.models import Delivery
        for group in self.all():
            deadline = group.last_deadline
            delivery = Delivery(
                deadline=deadline,
                delivery_type=deliverytypes.NON_ELECTRONIC,
                time_of_delivery=timezone.now())
            delivery.set_number()
            delivery.full_clean()
            delivery.save()

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
            subjectids_where_is_admin_queryset = Subject.objects\
                .filter_user_is_admin(user=user)\
                .values_list('id', flat=True)
            periodids_where_is_admin_queryset = PeriodPermissionGroup.objects \
                .filter(models.Q(permissiongroup__users=user))\
                .values_list('period_id', flat=True)
            return self.filter(
                # If anonymous, ignore periodadmins
                models.Q(
                    models.Q(
                        models.Q(parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS) |
                        models.Q(parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_FULLY_ANONYMOUS)
                    ) &
                    models.Q(parentnode__parentnode__parentnode_id__in=subjectids_where_is_admin_queryset)
                ) |

                # If not anonymous, include periodadmins
                models.Q(
                    models.Q(parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF) &
                    models.Q(
                        models.Q(parentnode__parentnode_id__in=periodids_where_is_admin_queryset) |
                        models.Q(parentnode__parentnode__parentnode_id__in=subjectids_where_is_admin_queryset)
                    )
                )
            )

    def filter_user_is_examiner(self, user):
        """
        Filter all :class:`.AssignmentGroup` objects where the given
        user is examiner.

        .. warning:: **Do not** use this to filter groups where an
            examiner has access. Use :meth:`.filter_examiner_has_access`.

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
        """
        Filter all :class:`.AssignmentGroup` objects within a published
        :class:`devilry.apps.core.models.Assignment`.
        """
        return self.filter(parentnode__publishing_time__lt=timezone.now())

    def filter_is_active(self):
        """
        Filter all :class:`.AssignmentGroup` objects within a published
        :class:`devilry.apps.core.models.Assignment` within an
        active :class:`devilry.apps.core.models.Period`.
        """
        now = timezone.now()
        return self.filter_is_published().filter(
            parentnode__parentnode__start_time__lt=now,
            parentnode__parentnode__end_time__gt=now)

    def filter_examiner_has_access(self, user):
        """
        Filter all :class:`.AssignmentGroup` objects where the given
        ``user`` has access as examiner.
        """
        return self.filter_is_active()\
            .filter(examiners__relatedexaminer__user=user,
                    examiners__relatedexaminer__active=True).distinct()

    def filter_student_has_access(self, user):
        """
        Filter all :class:`.AssignmentGroup` objects where the given
        ``user`` has access as student.
        """
        return self.filter_is_published().filter_user_is_candidate(user)

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

    def filter_periodtag_for_students(self, periodtag_id):
        """
        Filter :class:`.AssignmentGroup` by :class:`~.devilry.apps.core.models.period_tag.PeriodTag` for
        tags:class:`~.devilry.apps.core.models.relateduser.RelatedStudent`s.

        Args:
            periodtag_id: ID of a :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.
        """
        return self.filter(candidates__relatedstudent__periodtag__id=periodtag_id)

    def filter_periodtag_for_examiners(self, periodtag_id):
        """
        Filter :class:`.AssignmentGroup` by :class:`~.devilry.apps.core.models.period_tag.PeriodTag` for
        tags:class:`~.devilry.apps.core.models.relateduser.RelatedExaminers`s.

        Args:
            periodtag_id: ID of a :class:`~.devilry.apps.core.models.period_tag.PeriodTag`.
        """
        return self.filter(examiners__relatedexaminer__periodtag__id=periodtag_id)

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
        return self.annotate_with_number_of_published_feedbacksets() \
            .filter(
                models.Q(number_of_published_feedbacksets__gt=0) |
                models.Q(cached_data__public_total_comment_count__gt=0))

    def extra_annotate_with_fullname_of_first_candidate(self):
        # Not ment to be used directly - this is used by the
        # extra_order_by_fullname_of_first_candidate() method.
        return self.extra(
            select={
                "fullname_of_first_candidate": """
                    SELECT
                        LOWER(CONCAT(devilry_account_user.fullname, devilry_account_user.shortname))
                    FROM core_candidate
                    INNER JOIN core_relatedstudent
                        ON (core_relatedstudent.id = core_candidate.relatedstudent_id)
                    INNER JOIN devilry_account_user
                        ON (devilry_account_user.id = core_relatedstudent.user_id)
                    WHERE
                        core_candidate.assignment_group_id = core_assignmentgroup.id
                    ORDER BY LOWER(CONCAT(devilry_account_user.fullname, devilry_account_user.shortname)) ASC
                    LIMIT 1
                """
            },
        )

    def extra_order_by_fullname_of_first_candidate(self, descending=False):
        """
        Order by fullname of the first candidate (ordered by fullname) in each group.

        If the user does not have a fullname, we order by their shortname.
        All ordering is performed in lowercase.

        As the ``extra_`` prefix implies, this uses a fairly expensive custom SQL query
        added using the ``extra()``-method of the QuerySet.

        Args:
            descending: Set this to ``True`` to order descending.
        """
        if descending:
            order_by = ['-fullname_of_first_candidate']
        else:
            order_by = ['fullname_of_first_candidate']
        return self.extra_annotate_with_fullname_of_first_candidate().extra(
            order_by=order_by
        )

    def extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate(self):
        # Not ment to be used directly - this is used by the
        # extra_order_by_relatedstudents_anonymous_id_of_first_candidate() method.
        return self.extra(
            select={
                "relatedstudents_anonymous_id_of_first_candidate": """
                    SELECT
                        LOWER(CONCAT(core_relatedstudent.candidate_id, core_relatedstudent.automatic_anonymous_id))
                    FROM core_candidate
                    INNER JOIN core_relatedstudent
                        ON (core_relatedstudent.id = core_candidate.relatedstudent_id)
                    WHERE
                        core_candidate.assignment_group_id = core_assignmentgroup.id
                    ORDER BY
                        LOWER(CONCAT(core_relatedstudent.candidate_id, core_relatedstudent.automatic_anonymous_id))
                        ASC
                    LIMIT 1
                """
            },
        )

    def extra_order_by_relatedstudents_anonymous_id_of_first_candidate(self, descending=False):
        """
        Order by the anonymous ID of the RelatedStudent of the first candidate
        (ordered by the anonymous ID of the RelatedStudent of each candidate) in each group.

        Concatenates :obj:`devilry.apps.core.models.RelatedStudent.candidate_id` and
        :obj:`devilry.apps.core.models.RelatedUserBase.automatic_anonymous_id` (in that order)
        to generate the value to order on.

        This is intended to be used for ordering AssignmentGroups when
        the assignment is anonymous, and with :obj:`~devilry.apps.core.models.Assignment.uses_custom_candidate_ids`
        set to ``False``. If :obj:`~devilry.apps.core.models.Assignment.uses_custom_candidate_ids`
        is ``True``, use :meth:`.extra_order_by_candidates_candidate_id_of_first_candidate`.

        As the ``extra_`` prefix implies, this uses a fairly expensive custom SQL query
        added using the ``extra()``-method of the QuerySet.

        Args:
            descending: Set this to ``True`` to order descending.
        """
        if descending:
            order_by = ['-relatedstudents_anonymous_id_of_first_candidate']
        else:
            order_by = ['relatedstudents_anonymous_id_of_first_candidate']
        return self.extra_annotate_with_relatedstudents_anonymous_id_of_first_candidate().extra(
            order_by=order_by
        )

    def extra_annotate_with_candidates_candidate_id_of_first_candidate(self):
        # Not ment to be used directly - this is used by the
        # extra_order_by_candidates_candidate_id_of_first_candidate() method.
        return self.extra(
            select={
                "candidates_candidate_id_of_first_candidate": """
                    SELECT
                        core_candidate.candidate_id
                    FROM core_candidate
                    WHERE
                        core_candidate.assignment_group_id = core_assignmentgroup.id
                    ORDER BY core_candidate.candidate_id ASC
                    LIMIT 1
                """
            },
        )

    def extra_order_by_candidates_candidate_id_of_first_candidate(self, descending=False):
        """
        Order by the anonymous ID of the RelatedStudent of the first candidate
        (ordered by the anonymous ID of the RelatedStudent of each candidate) in each group.

        Concatenates :obj:`devilry.apps.core.models.RelatedStudent.candidate_id` and
        :obj:`devilry.apps.core.models.RelatedUserBase.automatic_anonymous_id` (in that order)
        to generate the value to order on.

        This is intended to be used for ordering AssignmentGroups when
        the assignment is anonymous, and with :obj:`~devilry.apps.core.models.Assignment.uses_custom_candidate_ids`
        set to ``True``. If :obj:`~devilry.apps.core.models.Assignment.uses_custom_candidate_ids`
        is ``False``, use :meth:`.extra_order_by_relatedstudents_anonymous_id_of_first_candidate`.

        As the ``extra_`` prefix implies, this uses a fairly expensive custom SQL query
        added using the ``extra()``-method of the QuerySet.

        Args:
            descending: Set this to ``True`` to order descending.
        """
        if descending:
            order_by = ['-candidates_candidate_id_of_first_candidate']
        else:
            order_by = ['candidates_candidate_id_of_first_candidate']
        return self.extra_annotate_with_candidates_candidate_id_of_first_candidate().extra(
            order_by=order_by
        )

    def extra_annotate_with_shortname_of_first_candidate(self):
        # Not ment to be used directly - this is used by the
        # extra_order_by_shortname_of_first_candidate() method.
        return self.extra(
            select={
                "shortname_of_first_candidate": """
                    SELECT
                        devilry_account_user.shortname
                    FROM core_candidate
                    INNER JOIN core_relatedstudent
                        ON (core_relatedstudent.id = core_candidate.relatedstudent_id)
                    INNER JOIN devilry_account_user
                        ON (devilry_account_user.id = core_relatedstudent.user_id)
                    WHERE
                        core_candidate.assignment_group_id = core_assignmentgroup.id
                    ORDER BY devilry_account_user.shortname ASC
                    LIMIT 1
                """
            },
        )

    def extra_order_by_shortname_of_first_candidate(self, descending=False):
        """
        Order by shortname of the first candidate (ordered by shortname) in each group.

        As the ``extra_`` prefix implies, this uses a fairly expensive custom SQL query
        added using the ``extra()``-method of the QuerySet.

        Args:
            descending: Set this to ``True`` to order descending.
        """
        if descending:
            order_by = ['-shortname_of_first_candidate']
        else:
            order_by = ['shortname_of_first_candidate']
        return self.extra_annotate_with_shortname_of_first_candidate().extra(
            order_by=order_by
        )

    def extra_annotate_with_lastname_of_first_candidate(self):
        # Not ment to be used directly - this is used by the
        # extra_order_by_lastname_of_first_candidate() method.
        return self.extra(
            select={
                "lastname_of_first_candidate": """
                    SELECT
                        devilry_account_user.lastname
                    FROM core_candidate
                    INNER JOIN core_relatedstudent
                        ON (core_relatedstudent.id = core_candidate.relatedstudent_id)
                    INNER JOIN devilry_account_user
                        ON (devilry_account_user.id = core_relatedstudent.user_id)
                    WHERE
                        core_candidate.assignment_group_id = core_assignmentgroup.id
                    ORDER BY devilry_account_user.lastname ASC
                    LIMIT 1
                """
            },
        )

    def extra_order_by_lastname_of_first_candidate(self, descending=False):
        """
        Order by lastname of the first candidate (ordered by lastname) in each group.

        As the ``extra_`` prefix implies, this uses a fairly expensive custom SQL query
        added using the ``extra()``-method of the QuerySet.

        Args:
            descending: Set this to ``True`` to order descending.
        """
        if descending:
            order_by = ['-lastname_of_first_candidate']
        else:
            order_by = ['lastname_of_first_candidate']
        return self.extra_annotate_with_lastname_of_first_candidate().extra(
            order_by=order_by
        )

    def extra_annotate_datetime_of_last_admin_comment(self):
        """
        Annotate with the datetiem of the last comment added by an admin.

        .. warning:: As the ``extra_`` prefix implies, this uses a
            custom SQL query added using the ``extra()``-method of the QuerySet.
            This query is fairly expensive.
        """
        from devilry.devilry_group.models import AbstractGroupComment
        return self.extra(
            select={
                "datetime_of_last_admin_comment": """
                    SELECT
                        devilry_comment_comment.published_datetime
                    FROM devilry_group_feedbackset
                    LEFT OUTER JOIN devilry_group_groupcomment
                        ON (devilry_group_groupcomment.feedback_set_id = devilry_group_feedbackset.id)
                    INNER JOIN devilry_comment_comment
                        ON (devilry_comment_comment.id = devilry_group_groupcomment.comment_ptr_id)
                    WHERE
                        devilry_group_feedbackset.group_id = core_assignmentgroup.id
                        AND
                        devilry_comment_comment.user_role = %s
                        AND
                        devilry_group_groupcomment.visibility <> %s
                    ORDER BY devilry_comment_comment.published_datetime DESC
                    LIMIT 1
                """
            },
            select_params=[
                Comment.USER_ROLE_ADMIN,
                AbstractGroupComment.VISIBILITY_PRIVATE,
            ]
        )

    def extra_order_by_datetime_of_last_admin_comment(self, descending=False):
        """
        Order by datetime of the last comment by an admin in each group.

        .. warning:: As the ``extra_`` prefix implies, this uses a
            custom SQL query added using the ``extra()``-method of the QuerySet.
            This query is fairly expensive.

        Args:
            descending: Set this to ``True`` to order descending.
        """
        if descending:
            order_by = ['-datetime_of_last_admin_comment']
        else:
            order_by = ['datetime_of_last_admin_comment']
        return self.extra_annotate_datetime_of_last_admin_comment().extra(
            order_by=order_by
        )

    def annotate_with_number_of_private_groupcomments_from_user(self, user):
        """
        Annotate the queryset with ``number_of_private_groupcomments_from_user`` -
        the number of :class:`devilry.devilry_group.models.GroupComment`
        with private :obj:`~devilry.devilry_group.models.GroupComment.visibility`
        added by the provided ``user``.
        Args:
            user: A User object.
        """
        from devilry.devilry_group.models import GroupComment
        return self.annotate(
            number_of_private_groupcomments_from_user=models.Count(
                models.Case(
                    models.When(feedbackset__groupcomment__visibility=GroupComment.VISIBILITY_PRIVATE,
                                feedbackset__groupcomment__user=user,
                                then=1)
                )
            )
        )

    def annotate_with_number_of_private_imageannotationcomments_from_user(self, user):
        """
        Annotate the queryset with ``number_of_private_imageannotationcomments_from_user`` -
        the number of :class:`devilry.devilry_group.models.ImageAnnotationComment`
        with private :obj:`~devilry.devilry_group.models.ImageAnnotationComment.visibility`
        added by the provided ``user``.
        Args:
            user: A User object.
        """
        from devilry.devilry_group.models import ImageAnnotationComment
        return self.annotate(
            number_of_private_imageannotationcomments_from_user=models.Count(
                models.Case(
                    models.When(feedbackset__imageannotationcomment__visibility=ImageAnnotationComment.VISIBILITY_PRIVATE,
                                feedbackset__imageannotationcomment__user=user,
                                then=1)
                )
            )
        )

    def prefetch_assignment_with_points_to_grade_map(self, assignmentqueryset=None):
        """
        Prefetches the assignment in the ``prefetched_assignment`` attribute.
        The prefetched assignment uses
        :meth:`devilry.apps.core.models.AssignmentQuerySet.prefetch_point_to_grade_map`, which
        means that each group in the queryset has an attribute named ``prefetched_assignment``,
        and that attribute is an Assignment object with the PointToGradeMap prefetched.

        Args:
            assignmentqueryset: The base assignment queryset. Defaults to ``Assignment.objects.all()``.
                Can be used to do further queries on the assignment queryset.
        """
        if not assignmentqueryset:
            assignmentqueryset = Assignment.objects.all()
        assignmentqueryset = assignmentqueryset.prefetch_point_to_grade_map()
        return self.prefetch_related(models.Prefetch('parentnode',
                                                     queryset=assignmentqueryset,
                                                     to_attr='prefetched_assignment'))

    def annotate_with_is_waiting_for_feedback_count(self):
        """
        Annotate the queryset with ``annotated_is_waiting_for_feedback``.
        Groups waiting for feedback is all groups where
        the deadline of the last feedbackset (or :attr:`.Assignment.first_deadline` and only one feedbackset)
        has expired, and the feedbackset does not have a
        :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`.

        This means that this method annotates with the same logic
        as the :meth:`.AssignmentGroup.is_waiting_for_feedback` property.

        Typically used for filtering by the annotated value. When you
        just need the information and have as AssignmentGroup object,
        you should use the :meth:`.AssignmentGroup.is_waiting_for_feedback` property.
        """
        now = timezone.now()
        whenquery = models.Q(
            cached_data__last_feedbackset__grading_published_datetime__isnull=True,
            cached_data__last_feedbackset__deadline_datetime__lt=now
        )

        return self.annotate(
            annotated_is_waiting_for_feedback=models.Count(
                models.Case(
                    models.When(whenquery, then=1)
                )
            )
        )

    def annotate_with_is_waiting_for_deliveries_count(self):
        """
        Annotate the queryset with ``annotated_is_waiting_for_deliveries``.
        Groups waiting for deliveries is all groups where
        the deadline of the last feedbackset (or :attr:`.Assignment.first_deadline` and only one feedbackset)
        has not expired, and the feedbackset does not have a
        :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`.

        This means that this method annotates with the same logic
        as the :meth:`.AssignmentGroup.is_waiting_for_deliveries` property.

        Typically used for filtering by the annotated value. When you
        just need the information and have as AssignmentGroup object,
        you should use the :meth:`.AssignmentGroup.is_waiting_for_deliveries` property.
        """
        now = timezone.now()
        whenquery = models.Q(
            cached_data__last_feedbackset__grading_published_datetime__isnull=True
        ) & (
            models.Q(
                ~models.Q(cached_data__last_feedbackset=models.F('cached_data__first_feedbackset')),
                models.Q(cached_data__last_feedbackset__deadline_datetime__gte=now),
            ) |
            models.Q(
                models.Q(cached_data__last_feedbackset=models.F('cached_data__first_feedbackset')),
                parentnode__first_deadline__gte=now
            )
        )
        return self.annotate(
            annotated_is_waiting_for_deliveries=models.Count(
                models.Case(
                    models.When(whenquery, then=1)
                )
            )
        )

    def annotate_with_is_corrected_count(self):
        """
        Annotate the queryset with ``annotated_is_corrected``.

        Corrected groups is all groups where the last feedbackset is
        the same as the last published feedbackset.

        This means that this method annotates with the same logic
        as the :meth:`.AssignmentGroup.is_corrected` property.

        Typically used for filtering by the annotated value. When you
        just need the information and have as AssignmentGroup object,
        you should use the :meth:`.AssignmentGroup.is_corrected` property.
        """
        whenquery = models.Q(
            models.Q(cached_data__last_feedbackset=models.F(
                'cached_data__last_published_feedbackset')),
        )
        return self.annotate(
            annotated_is_corrected=models.Count(
                models.Case(
                    models.When(whenquery, then=1)
                )
            )
        )

    def annotate_with_is_passing_grade_count(self):
        """
        Annotate the queryset with ``is_passing_grade``.
        ``is_passing_grade`` is ``True`` if the following is true
        if the last :class:`~devilry.devilry_group.models.FeedbackSet` in the group:
        - Is published.
        - Has :obj:`~devilry.devilry_group.models.FeedbackSet.grading_points`
          greater or equal to ``passing_grade_min_points`` for the
          :class:`.devilry.apps.core.models.Assignment`.
        """
        return self.annotate(
            is_passing_grade=models.Count(
                models.Case(
                    models.When(
                        cached_data__last_published_feedbackset__isnull=False,
                        cached_data__last_published_feedbackset__grading_points__gte=models.F(
                            'parentnode__passing_grade_min_points'),
                        then=1
                    ),
                    default=models.Value(None)
                )
            )
        )

    def annotate_with_has_unpublished_feedbackdraft_count(self):
        """
        Annotate the queryset with ``annotated_has_unpublished_feedbackdraft``.
        A group is considered to have an unpublished feedback draft if the following
        is true:
        - :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime` is ``None``.
        - :obj:`~devilry.devilry_group.models.FeedbackSet.grading_points` is not ``None``.
        So this means that all groups annotated with ``has_unpublished_feedbackdraft``
        are groups that are corrected, and ready be be published.


        This means that this method annotates with the same logic
        as the :meth:`.AssignmentGroup.has_unpublished_feedbackdraft` property.

        Typically used for filtering by the annotated value. When you
        just need the information and have as AssignmentGroup object,
        you should use the :meth:`.AssignmentGroup.has_unpublished_feedbackdraft` property.

        """
        whenquery = models.Q(
            cached_data__last_feedbackset__grading_published_datetime__isnull=True,
            cached_data__last_feedbackset__grading_points__isnull=False)
        return self.annotate(
            annotated_has_unpublished_feedbackdraft=models.Count(
                models.Case(models.When(whenquery, then=1))
            )
        )

    def delete(self, *args, **kwargs):
        self.update(internal_is_being_deleted=True)
        return super(AssignmentGroupQuerySet, self).delete(*args, **kwargs)


class AssignmentGroupManager(models.Manager):
    """
    Manager for :class:`.AssignmentGroup`.
    """

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
                relatedstudent=relatedstudent,
                assignment_group=group)
            candidates.append(candidate)
        Candidate.objects.bulk_create(candidates)

    def __bulk_update_feedbacksets(self, group_list, created_by_user):
        from devilry.devilry_group.models import FeedbackSet
        FeedbackSet.objects.filter(group__in=group_list).update(created_by=created_by_user)

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
            django.db.models.QuerySet: A queryset with the created groups.
        """
        batchoperation = BatchOperation.objects.create_synchronous(
            context_object=assignment,
            operationtype='create-groups-with-candidate-and-feedbackset')
        group_queryset = self.__bulk_create_groups(assignment=assignment,
                                                   batchoperation=batchoperation,
                                                   relatedstudents=relatedstudents)
        # We iterate over the groups multiple times, so we do this to avoid multiple queries
        group_list = list(group_queryset)

        self.__bulk_create_candidates(group_list=group_list,
                                      relatedstudents=relatedstudents)
        self.__bulk_update_feedbacksets(created_by_user=created_by_user,
                                        group_list=group_list)
        batchoperation.finish()
        return group_queryset


class AssignmentGroup(models.Model, AbstractIsAdmin, AbstractIsExaminer, Etag):
    """
    Represents a student or a group of students.

    .. attribute:: parentnode

        A django.db.models.ForeignKey_ that points to the parent node,
        which is always an Assignment.

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

    .. attribute:: cached_data

        A Django RelatedManager of :class:`cached_data <devilry.devilry_dbcache.models.AssignmentGroupCachedData>` for this AssignmentGroup.

    .. attribute:: feedbackset

        A Django RelatedManager :class:`devilry.apps.core.models.FeedbackSet` for this AssignmentGroup

    Note:
        Postgres triggers create a :class:`devilry.apps.core.models.FeedbackSet` on INSERT

    """

    objects = AssignmentGroupManager.from_queryset(AssignmentGroupQuerySet)()

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

    # NEVER set this yourself!
    # This field is used internally to make delete triggers related
    # to AssignmentGroupCachedData work. The reason for this need is
    # that Django changed how they handle delete in 1.10, so instead
    # of cascading deletes, they use the Collector class to delete
    # child objects (and send out the correct signals). This means that
    # child objects, such as Examiner objects is deleted before
    # the AssignmentGroup, and the triggers have no way to know
    # that this happens as part of an AssignmentGroup delete.
    # To work around this issue, we set this in AssignmentGroupQuerySet.delete()
    # and AssignmentGroup.delete() before we delete the AssignmentGroup.
    internal_is_being_deleted = models.BooleanField(default=False, editable=False)

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
    def q_is_candidate(cls, user_obj):
        """
        Returns a django.models.Q object matching AssignmentGroups where
        the given student is candidate.
        """
        return Q(candidates__relatedstudent__user=user_obj)

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
        now = timezone.now()
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
    def last_feedbackset_is_published(self):
        return self.cached_data.last_feedbackset.grading_published_datetime is not None

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
            candidateids.append(unicode(candidate.get_anonymous_name(assignment=assignment)))
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

    def get_short_displayname(self, assignment=None):
        assignment = assignment or self.assignment
        if assignment.is_anonymous:
            return self.get_anonymous_displayname(assignment=assignment)
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
    def short_displayname(self):
        """
        A short displayname for the group. If the assignment is anonymous,
        we list the candidate IDs. If the group has a name, the name is used,
        else we fall back to a comma separated list of usernames. If the group has no name and no
        students, we use the ID.

        .. seealso:: https://github.com/devilry/devilry-django/issues/498
        """
        return self.get_short_displayname()

    def get_unanonymized_long_displayname(self):
        candidates = self.candidates.all()
        names = [candidate.relatedstudent.user.get_full_name() for candidate in candidates]
        out = u', '.join(names)
        if not out:
            out = self.__get_no_candidates_nonanonymous_displayname()
        if self.name:
            out = u'{} ({})'.format(self.name, out)
        return out

    def get_long_displayname(self, assignment=None):
        """
        A long displayname for the group. If the assignment is anonymous,
        we list the candidate IDs.

        If the assignment is not anonymous, we use a comma separated list of
        the displaynames (full names with fallback to shortname) of the
        students. If the group has a name, we use the groupname with the names
        of the students in parenthesis.

        .. seealso:: https://github.com/devilry/devilry-django/issues/499
        """
        assignment = assignment or self.assignment
        if assignment.is_anonymous:
            out = self.get_anonymous_displayname(assignment=assignment)
        else:
            out = self.get_unanonymized_long_displayname()
        return out

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
        return self.get_long_displayname()

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
        copy everything assignment group contains into a new AssignmentGroup,
        except candiates.

        Returns:
            :class:`~core.AssignmentGroup` a new assignmentgroup
        """
        groupcopy = AssignmentGroup(parentnode=self.parentnode,
                                    name=self.name,
                                    is_open=self.is_open,
                                    delivery_status=self.delivery_status)
        groupcopy.full_clean()
        groupcopy.save()
        for examiner in self.examiners.all():
            groupcopy.examiners.create(relatedexaminer=examiner.relatedexaminer)
        for tagobj in self.tags.all():
            groupcopy.tags.create(tag=tagobj.tag)
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

    def _merge_tags_into(self, target):
        """
        Move tags to ``target`` AssignmentGroup.
        if tag is present in ``target`` AssignmentGroup remove tag from db

        Args:
            target: :class:`~core.AssignmentGroup` to be merged into

        """
        for tag in self.tags.all():
            if target.tags.filter(tag=tag.tag).exists():
                tag.delete()
            else:
                tag.assignment_group = target
                tag.save()

    def _merge_examiners_into(self, target):
        """
        Move examiners to ``target`` AssignmentGroup.
        if examier is present in ``target`` AssignmentGroup remove examiner from db

        Args:
            target: :class:`~core.AssignmentGroup` to be merged into

        """
        for examiner in self.examiners.all():
            if target.examiners.filter(relatedexaminer__user_id=examiner.relatedexaminer.user_id).exists():
                examiner.delete()
            else:
                examiner.assignmentgroup = target
                examiner.save()

    def _merge_candidates_into(self, target):
        """
        Move candidates to ``target`` AssignmentGroup.
        if candidate is present in ``target`` AssignmentGroup remove candidate from db

        Args:
            target: :class:`~core.AssignmentGroup` to be merged into

        """
        for candidate in self.candidates.all():
            if target.candidates.filter(relatedstudent__user_id=candidate.relatedstudent.user_id).exists():
                candidate.delete()
            else:
                candidate.assignment_group = target
                candidate.save()

    def _merge_feedbackset_into(self, target):
        """
        Merge feedbacksets from self to target.

        Algorithm:
            - Merge self feedbacksets into target AssignmentGroup and set feedbackset type to merge prefix
            - For first Feedbackset we have to set the deadline since it's None by default

        Args:
            target: :class:`~core.AssignmentGroup` to be merged into
        """
        from devilry.devilry_group.models import FeedbackSet

        # Map feedbackset_type to merge prefix
        feedbackset_type_merge_map = {
            FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT: FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT,
            FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT: FeedbackSet.FEEDBACKSET_TYPE_MERGE_NEW_ATTEMPT,
            FeedbackSet.FEEDBACKSET_TYPE_RE_EDIT: FeedbackSet.FEEDBACKSET_TYPE_MERGE_RE_EDIT
        }

        feedbacksets = self.feedbackset_set.order_by_deadline_datetime()\
            .select_related('group__parentnode')

        for feedbackset in feedbacksets:
            # change feedbackset_type to merge prefix
            if feedbackset.feedbackset_type in feedbackset_type_merge_map.keys():
                feedbackset.feedbackset_type = feedbackset_type_merge_map[feedbackset.feedbackset_type]
            feedbackset.group = target
            feedbackset.save()

    def merge_into(self, target):
        """
        Merge this AssignmentGroup into ``target`` AssignmentGroup

        - Move all feedbacksets into target AssignmentGroup
        - Move in all candidates not already on the AssignmentGroup.
        - Move in all examiners not already on the AssignmentGroup.
        - Move in all tags not already on the AssignmentGroup.
        - delete this AssignmentGroup

        Args:
            target: :class:`~core.AssignmentGroup` the assignment group that self will be merged into

        Raises:
            ValueError if self and target AssignmentGroup is not part of same Assignment

        Returns:

        """
        self._merge_feedbackset_into(target)
        self._merge_candidates_into(target)
        self._merge_examiners_into(target)
        self._merge_tags_into(target)
        self.delete()

    def can_merge(self, target):
        """
        Checks whether we can merge into target
        Args:
            target: :class:`~core.AssignmentGroup` target assignment group

        Raises:
            ValidationError
        """
        if self.parentnode_id != target.parentnode_id:
            raise ValidationError(
                _('Cannot merge self into target, self and target is not part of same AssignmentGroup')
            )

    def set_all_target_feedbacksets_to_merge_type(self, target):
        """
        Set all FeedbackSet types to it's corresponding merge type for the target group.

        Args:
            target: :class:`~core.AssignmentGroup` the assignment group to add new feedbackset to.
        """
        from devilry.devilry_group.models import FeedbackSet

        # Map feedbackset_type to merge prefix
        feedbackset_type_merge_map = {
            FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT: FeedbackSet.FEEDBACKSET_TYPE_MERGE_FIRST_ATTEMPT,
            FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT: FeedbackSet.FEEDBACKSET_TYPE_MERGE_NEW_ATTEMPT,
            FeedbackSet.FEEDBACKSET_TYPE_RE_EDIT: FeedbackSet.FEEDBACKSET_TYPE_MERGE_RE_EDIT
        }
        for feedbackset in target.feedbackset_set.all():
            if feedbackset.feedbackset_type in feedbackset_type_merge_map.keys():
                feedbackset.feedbackset_type = feedbackset_type_merge_map[feedbackset.feedbackset_type]
                feedbackset.save()

    def create_new_first_attempt_for_target_group(self, target):
        """
        Create a new FeedbackSet with type ``first_attempt`` for target group.

        Args:
            target: :class:`~core.AssignmentGroup` the assignment group to add new feedbackset to.
        """
        from devilry.devilry_group.models import FeedbackSet
        last_deadline = target.feedbackset_set.order_by('-deadline_datetime').first().deadline_datetime
        last_deadline = last_deadline + timezone.timedelta(microseconds=1)
        new_feedbackset = FeedbackSet(
            group=target, feedbackset_type=FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT,
            deadline_datetime=last_deadline)
        new_feedbackset.full_clean()
        new_feedbackset.save()

    @classmethod
    def merge_groups(self, groups):
        """
        First group will be target assignment group, the rest of the groups in the list
        will be merged into target.

        For further explanation see: :ref:`assignmentgroup_merge`
        Args:
            groups: list with :class:`~core.AssignmentGroup`

        Raises:
            ValidationError if we are not able to merge groups
        """
        if len(groups) < 2:
            raise ValidationError(_('Cannot merge less than 2 groups'))

        from devilry.apps.core.models import AssignmentGroupHistory

        target_group = groups.pop(0)
        # Check if we can merge
        for group in groups:
            group.can_merge(target_group)

        # Create or get target group history
        try:
            grouphistory = target_group.assignmentgrouphistory
        except AssignmentGroupHistory.DoesNotExist:
            grouphistory = AssignmentGroupHistory(assignment_group=target_group)
        # Insert groups in history
        grouphistory.merge_assignment_group_history(groups)

        # Merge groups
        with transaction.atomic():
            for group in groups:
                group.merge_into(target=target_group)
                group.set_all_target_feedbacksets_to_merge_type(target=target_group)
                group.create_new_first_attempt_for_target_group(target=target_group)
            grouphistory.save()

    def pop_candidate(self, candidate):
        """
        Pops a candidate off the assignment group.
        Copy this Assignment group and all inherent Feedbacksets and comments

        Args:
            candidate: :class:`~core.Candidate`

        Raises:
            GroupPopNotCandiateError when candiate is not part of AssignmentGroup

        Returns:

        """
        if not self.candidates.filter(id=candidate.id).exists():
            raise GroupPopNotCandidateError('candidate is not part of AssignmentGroup')
        if len(self.candidates.all()) < 2:
            raise GroupPopToFewCandidatesError('cannot pop candidate from AssignmentGroup when there is only one')

        groupcopy = self.copy_all_except_candidates()
        candidate.assignment_group = groupcopy
        candidate.save()
        self.cached_data.first_feedbackset.copy_feedbackset_into_group(
            group=groupcopy,
            target=groupcopy.cached_data.first_feedbackset
        )
        for feedbackset in self.feedbackset_set.order_by_deadline_datetime():
            if feedbackset != self.cached_data.first_feedbackset:
                feedbackset.copy_feedbackset_into_group(group=groupcopy)

    def get_current_state(self):
        """
        Dumps the current state of this AssignmentGroup and all inherent models such as
        user.id of candidates and examiners, tags and feedbacksets into a dictionary.

        Returns:
            dictonary with current state of assignmentGroup and all inherent models
        """
        candidate_queryset = self.candidates.all().select_related('relatedstudent')
        candidates = [candidate.relatedstudent.user_id for candidate in candidate_queryset]
        examiner_queryset = self.examiners.all().select_related('relatedexaminer')
        examiners = [examiner.relatedexaminer.user_id for examiner in examiner_queryset]
        tag_queryset = self.tags.all()
        tags = [tag.tag for tag in tag_queryset]
        feedbackset_queryset = self.feedbackset_set.order_by_deadline_datetime().prefetch_related('groupcomment_set')
        feedbacksets = [feedbackset.id for feedbackset in feedbackset_queryset]

        return {
            'name': self.name,
            'created_datetime': self.created_datetime.isoformat(),
            'candidates': candidates,
            'examiners': examiners,
            'tags': tags,
            'feedbacksets': feedbacksets,
            'parentnode': self.parentnode.id
        }

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
                now = timezone.now()
                if self.last_deadline.deadline > now:
                    return 'waiting-for-deliveries'
                else:
                    return 'waiting-for-feedback'
        else:
            return self.delivery_status

    def get_all_admin_ids(self):
        warnings.warn("deprecated", DeprecationWarning)
        return self.parentnode.get_all_admin_ids()

    @property
    def published_grading_points(self):
        """
        Get the :obj:`~devilry.devilry_group.models.FeedbackSet.grading_points`
        from the last **published** :class:`devilry.devilry_group.models.FeedbackSet`.

        This means that this property returns the current public grade for the AssignmentGroup.
        """
        if self.cached_data.last_published_feedbackset_id is None:
            return None
        else:
            return self.cached_data.last_published_feedbackset.grading_points

    @property
    def drafted_grading_points(self):
        """
        Get the :obj:`~devilry.devilry_group.models.FeedbackSet.grading_points`
        from the last :class:`devilry.devilry_group.models.FeedbackSet` if the
        last feedbackset is not the same as the published feedbackset.

        If the last published feedbackset is the same as the last feedbackset,
        this always returns ``None``. This will also return ``None`` if the
        last feedbackset does not have a grade yet.
        """
        cached_data = self.cached_data
        if cached_data.last_published_feedbackset_is_last_feedbackset:
            return None
        else:
            return self.cached_data.last_feedbackset.grading_points

    @property
    def published_grade_is_passing_grade(self):
        """
        Returns ``True`` if :meth:`.published_grading_points` is a passing
        grade.
        """
        if self.published_grading_points is None:
            return False
        else:
            return self.published_grading_points >= self.assignment.passing_grade_min_points

    @property
    def has_unpublished_feedbackdraft(self):
        """
        A group is considered to have an unpublished feedback draft if the following
        is true for the last feedbackset:

        - :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime` is ``None``.
        - :obj:`~devilry.devilry_group.models.FeedbackSet.grading_points` is not ``None``.

        So this means that if this property returns ``True``, the group
        is corrected, and ready be be published.
        """
        last_feedbackset = self.cached_data.last_feedbackset
        return (last_feedbackset.grading_published_datetime is None
                and last_feedbackset.grading_points is not None)

    @property
    def is_corrected(self):
        """
        Returns ``True`` if the last feedbackset is published.
        """
        return self.cached_data.last_published_feedbackset_is_last_feedbackset

    @property
    def is_waiting_for_feedback(self):
        """
        Groups waiting for feedback is all groups where
        the deadline of the last feedbackset (or :attr:`.Assignment.first_deadline` and only one feedbackset)
        has expired, and the feedbackset does not have a
        :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`.
        """
        if self.is_corrected:
            return False
        return self.cached_data.last_feedbackset_deadline_datetime < timezone.now()

    @property
    def is_waiting_for_deliveries(self):
        """
        Groups waiting for deliveries is all groups where
        the deadline of the last feedbackset (or :attr:`.Assignment.first_deadline` and only one feedbackset)
        has not expired, and the feedbackset does not have a
        :obj:`~devilry.devilry_group.models.FeedbackSet.grading_published_datetime`.
        """
        if self.is_corrected:
            return False
        return self.cached_data.last_feedbackset_deadline_datetime >= timezone.now()

    def delete(self, *args, **kwargs):
        self.internal_is_being_deleted = True
        self.save()
        return super(AssignmentGroup, self).delete(*args, **kwargs)


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
