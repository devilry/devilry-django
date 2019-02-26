from devilry.utils import OrderedDict
from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet
import json


# class GroupList(list):
#     """
#     Represents a list of :class:`devilry.apps.core.models.AssignmentGroup` objects,
#     with utility functions for commonly needed actions. The list is ment to hold
#     groups where the same student in candidate on a single assignment, and the
#     utilities is ment to make it easier to work with the added complexity of
#     supporting the same user in multiple groups on a single assignment.
#     """
#     def get_feedback_with_most_points(self):
#         """
#         Get the :class:`devilry.apps.core.models.StaticFeedback` with the most points in the list.
#         """
#         best = None
#         for group in self:
#             feedback = None
#             if group.get_status() == 'corrected':
#                 feedback = group.feedback
#             if best:
#                 if feedback and feedback.points > best.points:
#                     best = group
#             else:
#                 best = feedback
#         return best
#
#     def get_best_gradestring(self):
#         """
#         Uses :meth:`.get_feedback_with_most_points` to get the feedback with most points,
#         and returns the ``grade``-attribute of that feedback.
#
#         :return: The grade or ``None``.
#         """
#         best = self.get_feedback_with_most_points()
#         if best:
#             return best.grade
#         else:
#             return None
#
#     def _serialize_feedback(self, feedback):
#         if feedback:
#             return {'id': feedback.id,
#                     'grade': feedback.grade,
#                     'points': feedback.points,
#                     'is_passing_grade': feedback.is_passing_grade,
#                     'save_timestamp': feedback.save_timestamp}
#         else:
#             return None
#
#     def _serialize_group(self, group):
#         return {
#             'id': group.id,
#             'feedback': self._serialize_feedback(group.feedback),
#             'status': group.get_status()
#         }
#
#     def serialize(self):
#         return [self._serialize_group(group) for group in self]


class FeedbackSetList(list):

    def append(self, p_object):
        """

        Args:
            p_object:

        Returns:

        """
        if not isinstance(p_object, FeedbackSet):
            raise ValueError('Appended object must be instance of FeedbackSet')
        super(FeedbackSetList, self).append(p_object)

    def get_feedbackset_with_most_points(self):
        """
        Get the :obj:`~.devilry.devilry_group.models.FeedbackSet` with the most points.

        Returns:
             :obj:`~.devilry.devilry_group.models.FeedbackSet` or None.
        """
        best = None
        for feedbackset in self:
            if not best:
                best = feedbackset
            elif best.grading_points < feedbackset.grading_points:
                best = feedbackset
        return best


class GroupFeedbackSetList(list):
    """
    A list of tuples containing :class:`devilry.apps.core.models.AssignmentGroup` and
    :class:`devilry.devilry_group.models.FeedbackSet` objects.

    The ``FeedbackSet`` is associated with the AssignmentGroup in the tuple by its foreignkey(``FeedbackSet.group``)
    and is the last ``FeedbackSet`` for the group(``FeedbackSet.is_last_in_group == True``).
    """
    def append(self, p_object):
        """
        Overrides append for errorhandling. Make object to add is a tuple of :class:`~devilry.apps.core.models.AssignmentGroup`
        and :class:`~devilry.devilry_group.models.FeedbackSet`.

        Args:
            p_object: Tuple (AssignmentGroup, FeedbackSet) to add.

        Raises:
            ValueError: If `p_object` is not a tuple, or if the tuple does not consist of a
                ``AssignmentGroup`` or ``FeedbackSet``.
        """
        if not isinstance(p_object, tuple):
            raise ValueError('Appended object must be a tuple of objects (AssignmentGroup, FeedbackSet).')
        group, feedbackset = p_object
        if not isinstance(group, AssignmentGroup) or not isinstance(feedbackset, FeedbackSet):
            raise ValueError('Objects in tuple must be of (AssignmentGroup, FeedbackSet) in that order.')
        super(GroupFeedbackSetList, self).append(p_object)

    def get_feedbackset_with_most_points(self):
        """
        Get the :obj:`~.devilry.devilry_group.models.FeedbackSet` with the most points.

        Returns:
             :obj:`~.devilry.devilry_group.models.FeedbackSet` or None.
        """
        best = None
        for group, feedbackset in self:
            if not best:
                best = feedbackset
            elif best.grading_points < feedbackset.grading_points:
                best = feedbackset
        return best

    def _serialize_feedbackset(self, feedbackset):
        """
        Serialize the given ``feedbackset`` as dictionary format.

        Args:
            feedbackset: ``FeedbackSet`` to serialize.

        Returns:
            dict: Serialized dictionary of ``feedbackset``, or 'None' if ``feedbackset`` is 'None'
        """
        if feedbackset:
            return {'id': feedbackset.id,
                    'grade': 'NA',
                    'points': feedbackset.grading_points,
                    'published_by': feedbackset.grading_published_by,
                    'published': feedbackset.grading_published_datetime,
                    'deadline': feedbackset.current_deadline()}
        else:
            return None

    def _serialize_group(self, group, feedbackset):
        """
        Serialize the given ``group``
        Args:
            group:
            feedbackset:

        Returns:

        """
        return {'id': group.id,
                'feedbackset': self._serialize_feedbackset(feedbackset),
                'status': group.get_status()}

    def serialize(self):
        return [self._serialize_group(group, feedbackset) for group, feedbackset in self]


class AggregatedRelatedStudentInfo(object):
    """
    Used by :class:`.GroupsGroupedByRelatedStudentAndAssignment` to store all results for a
    single student on a period.
    """
    def __init__(self, user, assignments, relatedstudent=None):
        #: The Django user object for the student.
        self.user = user

        #: Dict of assignments where the key is the assignment-id, and the value is a :class:`.GroupFeedbacksetList`.
        self.assignments = assignments

        #: The :class:`devilry.apps.core.models.RelatedStudent` for users that are related students.
        #: This is only available for the objects returned by
        #: :meth:`.GroupsGroupedByRelatedStudentAndAssignment.iter_relatedstudents_with_results`,
        #: and not for the objects returned by the ignored students iterators.
        self.relatedstudent = relatedstudent

    def iter_groups_feedbacksets_by_assignment(self):
        """
        Returns an iterator over all :class:`.GroupFeedbackSetList` objects for this student.
        Shortcut for ``self.assignments.itervalues()``.
        """
        return iter(self.assignments.values())

    def add_group_with_feedbackset(self, group):
        """
        Used by :class:`.GroupsGroupedByRelatedStudentAndAssignment` to add a group and the last
        FeedbackSet for the group.

        Args:
            group: AssignmentGroup to add.
        """
        last_feedbackset = group.cached_data.last_feedbackset
        self.assignments[group.parentnode.id].append((group, last_feedbackset))

    def student_qualifies(self):
        """
        Check if the student qualifies for the final exam.

        If the student is NOT enlisted in one or more Assignments that are qualifying, e.g is
        in the ``assignments``-list, the student will NOT qualify.

        If the student is enlisted in all the qualifying Assignments, but does not have enough
        points to meet the requirements of :obj:`~devilry.app.core.models.Assignment.passing_grade_min_points` the
        student will NOT qualify.

        Returns:
            bool: ``True`` if student qualifies, else ``False``.
        """
        for groups_fbsets in self.assignments.values():
            if len(groups_fbsets) == 0:
                # Student not enlisted on assignment.
                return False
            for group, fbset in groups_fbsets:
                if not fbset.grading_published_datetime:
                    return False
                if fbset.grading_points < group.parentnode.passing_grade_min_points:
                    return False
        return True

    def prettyprint_with_feedbackset_grading(self):
        """
        Prettyprint for debugging.
        Uses FeedbackSet to fetch grading results.
        """
        qualifies = True
        print('\n{}\n{}'.format(self.user.fullname, self.user))
        for assignmentid, groups_fbsets in self.assignments.items():
            print('  - Assignment ID: {}'.format(assignmentid))
            print('     - Groups: {}'.format(len(groups_fbsets)))
            if len(groups_fbsets) == 0:
                qualifies = False
            for group, fbset in groups_fbsets:
                if fbset:
                    assignment_is_passed = fbset.grading_points >= group.parentnode.passing_grade_min_points
                    if not assignment_is_passed:
                        qualifies = False
                    grade = 'passed: {} (points:{}/{})'.format(
                            assignment_is_passed,
                            fbset.grading_points, group.parentnode.max_points)
                else:
                    grade = 'Grade not published'
                print('    - {}: {}'.format(group, grade))
                print('Qualifies: YES' if qualifies else 'Qualifies: NO')

    def prettyprint(self):
        """
        Prettyprint for debugging.
        """
        print('{}:'.format(self.user))
        for assignmentid, groups in self.assignments.items():
            print('  - Assignment ID: {}'.format(assignmentid))
            print('     - Groups: {}'.format(len(groups)))
            for group in groups:
                if group.feedback:
                    grade = '{} (points:{},passed:{})'.format(
                            group.feedback.grade,
                            group.feedback.points, group.feedback.is_passing_grade)
                else:
                    grade = None
                print('    - {}: {}'.format(group, grade))

    def __str__(self):
        """
        Returns a short representation of the object that should be useful when debugging.
        """
        results = ''
        for group_feedbackset_list in self.iter_groups_feedbacksets_by_assignment():
            for group, feedbackset in group_feedbackset_list:
                results += '\n\t\t{}: {}'.format(group.parentnode, feedbackset.grading_points)
        return 'AggregatedRelatedStudentInfo\n\tUser: {}\n\tAssignmentscount: {}\n\tResults: {}'.format(
            self.user.shortname,
            len(self.assignments),
            results
        )

    def _serialize_user(self):
        return {'id': self.user.id,
                'username': self.user.shortname,
                'fullname': self.user.fullname}

    def _serialize_relatedstudent(self):
        return{
            'id': self.relatedstudent.id,
            'tags': self.relatedstudent.tags,
            'candidate_id': self.relatedstudent.candidate_id
        }

    def _serialize_groups_by_assignment(self):
        groups_by_assignment_list = []
        for assignmentid, group_feedbackset in self.assignments.items():
            groups_by_assignment_list.append(
                    {'assignmentid': assignmentid,
                     'group_feedbackset_list': group_feedbackset.serialize()})
        return groups_by_assignment_list

    def serialize(self):
        out = {'id': self.user.id, # NOTE: This is added to support stupid datamodel layers, like ExtJS, which does not support the ID of a record to be within an attribute
               'user': self._serialize_user(),
               'groups_by_assignment': [],
               'relatedstudent': None}
        if self.relatedstudent:
            out['relatedstudent'] = self._serialize_relatedstudent()
        out['groups_by_assignment'] = self._serialize_groups_by_assignment()
        return out


class GroupsGroupedByRelatedStudentAndAssignment(object):
    """
    Provides an easy-to-use API for overviews over the results of all students
    in a period.
    """
    def __init__(self, period):
        #: The period the result info gathering is for.
        self.period = period

        #: The assignments that a student must pass.
        #: If ``None`` or all ids are passed, all assignments must be passed.
        # self.qualifying_assignment_ids = qualifying_assignment_ids

        #: All :obj:`devilry.apps.core.Assignment`s in `qualifying_assigment_ids` for the `period`.
        self.assignments = []

        #: All :obj:`devilry.apps.core.AssignmentGroup`s for the `qualifying_assigment_ids`.
        self.groups = []

        #: The result dictionary with relatedstudent.id as key and AggregatedRelatedStudentInfo as value.
        self.result = {}

        #: Ignored students.
        self.ignored_students = {}

        #: Ignored students with results.
        self.ignored_students_with_results = set()

        self._collect_assignments()
        self._collect_groups()
        self._initialize_result()
        self._add_groups_to_result()

    def get_assignment_queryset(self):
        """
        Get the queryset used to fetch all assignments on the period.
        Override for custom ordering or if you need to optimize the query for
        your usecase (``select_related``, ``prefetch_related``, etc.)
        """
        # assignment_queryset = self.period.assignments.all().order_by('publishing_time')
        # if self.qualifying_assignment_ids is not None:
        #     assignment_queryset = assignment_queryset\
        #         .filter(id__in=self.qualifying_assignment_ids)\
        #         .order_by('publishing_time')
        # return assignment_queryset
        return self.period.assignments.all().order_by('publishing_time')

    def get_relatedstudents_queryset(self):
        """
        Get the queryset used to fetch all relatedstudents on the period.
        Override if you need to optimize the query for your usecase
        (``select_related``, ``prefetch_related``, etc.)
        """
        return self.period.relatedstudent_set.all().select_related('user')

    def get_groups_queryset(self):
        """
        Get the queryset used to fetch all groups on the period.
        Override if you need to optimize the query for your usecase
        (``select_related``, ``prefetch_related``, etc.)
        """
        groupqry = AssignmentGroup.objects.filter(parentnode__parentnode=self.period)
        groupqry = groupqry.select_related('parentnode', 'parentnode__parentnode', 'feedback')
        groupqry = groupqry.prefetch_related('candidates', 'candidates__relatedstudent', 'deadlines')
        return groupqry

    def get_groups_queryset_with_prefetched_feedbacksets(self):
        """
        Note:
            Replaces old feedback and deadline fetching in get_groups_queryset.
            Removed deadline and feedback as this info is stored in FeedbackSet.

        Prefetches Assignments, Periods and FeedbackSets for the AssignmentGroups in the queryset.

        Returns:
            QuerySet: QuerySet of AssignmentGroups.
        """
        groupqry = AssignmentGroup.objects.filter(parentnode__parentnode=self.period)
        # if self.qualifying_assignment_ids is not None:
        #     groupqry = groupqry.filter(parentnode__id__in=self.qualifying_assignment_ids)
        groupqry = groupqry.select_related('parentnode', 'parentnode__parentnode')
        groupqry = groupqry.prefetch_related('candidates', 'candidates__relatedstudent', 'feedbackset_set')
        return groupqry

    def _collect_assignments(self):
        """
        Appends all :class:`~devilry.app.core.models.Assignment`s to `assignments` dict.
        """
        for assignment in self.get_assignment_queryset():
            self.assignments.append(assignment)

    def _collect_groups(self):
        """
        Appends all :class:`~devilry.app.core.models.AssignmentGroup`s to `groups` dict.
        """
        for group in self.get_groups_queryset_with_prefetched_feedbacksets():
            self.groups.append(group)

    def _create_assignmentsdict(self):
        dct = OrderedDict()
        for assignment in self.assignments:
            dct[assignment.id] = GroupFeedbackSetList()
        return dct

    def _initialize_result(self):
        """
        Initializes the result dictionary by adding a instance of :class:`~.AggregatedRelatedStudentInfo` for
        each student.
        """
        for relatedstudent in self.get_relatedstudents_queryset():
            self.result[relatedstudent.id] = AggregatedRelatedStudentInfo(
                user=relatedstudent.user,
                assignments=self._create_assignmentsdict(),
                relatedstudent=relatedstudent
            )

    def _create_or_add_ignoredgroup(self, ignoreddict, candidate):
        if candidate.candidate_id not in ignoreddict:
            ignoreddict[candidate.candidate_id] = AggregatedRelatedStudentInfo(
                user=candidate.relatedstudent,
                assignments=self._create_assignmentsdict()
            )
        return ignoreddict[candidate.candidate_id]

    def _add_groups_to_result(self):
        """
        Adds the AssignmentGroups to the result dictionary.
        """
        # groupqry = self.get_groups_queryset_with_prefetched_feedbacksets()
        for group in self.groups:
            for candidate in group.candidates.all():
                if candidate.relatedstudent.id in self.result:
                    self.result[candidate.relatedstudent.id].add_group_with_feedbackset(group)
                else:
                    self._create_or_add_ignoredgroup(self.ignored_students, candidate).\
                        add_group_with_feedbackset(group)
                    if group.feedback:
                        self.ignored_students_with_results.add(candidate.candidate_id)

    def iter_assignments(self):
        """
        Iterate over all the assignments, yielding Assignment-objects. The objects
        are iterated in the order returned by :meth:`get_assignment_queryset`.
        """
        return self.assignments.__iter__()

    def iter_relatedstudents_with_results(self):
        """
        Iterate over all relatedstudents, yielding a dict with the following attributes for each
        related student:

            user
                The Django user-object for the student.
            assignments
                An OrderedDict, ordered the same as :meth:`.iter_assignments`, where the key is
                the assignment-id, and the value is a list of AssignmentGroup-objects where the user
                is candidate. The list may have 0 or more groups, 0 if the user is not in any group
                on the assignment, and more than 1 if the user is in more than one group on the
                assignment.
        """
        return iter(self.result.values())

    def iter_students_that_is_candidate_but_not_in_related(self):
        """
        Iterate over the students that is candidate on one or more groups, but not registered as
        related students.

        This iterator includes everything yielded by both:

        - :meth:`iter_students_with_feedback_that_is_candidate_but_not_in_related`
        - :meth:`iter_students_with_no_feedback_that_is_candidate_but_not_in_related`
        """
        return iter(self.ignored_students.values())

    def iter_students_with_feedback_that_is_candidate_but_not_in_related(self):
        """
        Same as :meth:`.iter_students_that_is_candidate_but_not_in_related`, but it does not include
        the students that have no feedback.
        """
        for userid, aggregatedgroupinfo in self.ignored_students.items():
            if userid in self.ignored_students_with_results:
                yield aggregatedgroupinfo

    def iter_students_with_no_feedback_that_is_candidate_but_not_in_related(self):
        """
        Iterate over everything returned by
        :meth:`.iter_students_that_is_candidate_but_not_in_related`
        except for the students returned by
        :meth:`.iter_students_with_feedback_that_is_candidate_but_not_in_related`
        """
        for userid, aggregatedgroupinfo in self.ignored_students.items():
            if userid not in self.ignored_students_with_results:
                yield aggregatedgroupinfo

    def _serialize_assignment(self, basenode):
        return {'id': basenode.id,
                'short_name': basenode.short_name,
                'long_name': basenode.long_name}

    def serialize(self):
        """
        Serialize all the collected data as plain python objects.
        """
        out = {
            'relatedstudents':
                [r.serialize() for r in self.iter_relatedstudents_with_results()],
            'students_with_no_feedback_that_is_candidate_but_not_in_related':
                [r.serialize() for r in self.iter_students_with_no_feedback_that_is_candidate_but_not_in_related()],
            'students_with_feedback_that_is_candidate_but_not_in_related':
                [r.serialize() for r in self.iter_students_with_feedback_that_is_candidate_but_not_in_related()],
            'assignments':
                [self._serialize_assignment(a) for a in self.iter_assignments()]
        }
        return out
