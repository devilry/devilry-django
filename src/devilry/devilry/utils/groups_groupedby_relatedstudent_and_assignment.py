from devilry.utils import OrderedDict
from devilry.apps.core.models import AssignmentGroup



class GroupList(list):
    """
    Represents a list of :class:`devilry.apps.core.models.AssignmentGroup` objects,
    with utility functions for commonly needed actions. The list is ment to hold
    groups where the same student in candidate on a single assignment, and the
    utilities is ment to make it easier to work with the added complexity of
    supporting the same user in multiple groups on a single assignment.
    """
    def get_feedback_with_most_points(self):
        """
        Get the :class:`devilry.apps.core.models.StaticFeedback` with the most points in the list.
        """
        best = None
        for group in self:
            if best:
                if group.feedback and group.feedback.points > best.points:
                    best = group
            else:
                best = group.feedback
        return best

    def get_best_gradestring(self):
        """
        Uses :meth:`.get_feedback_with_most_points` to get the feedback with most points,
        and returns the ``grade``-attribute of that feedaback.

        :return: The grade or ``None``.
        """
        best = self.get_feedback_with_most_points()
        if best:
            return best.grade
        else:
            return None



class AggreatedRelatedStudentInfo(object):
    """
    Used by :class:`.GroupsGroupedByRelatedStudentAndAssignment` to stores all results for a
    single student on a period.
    """
    def __init__(self, user, assignments):
        #: The Django user object for the student.
        self.user = user

        #: Dict of assignments where the key is the assignment-id, and the value is a :class:`.GroupList`.
        self.assignments = assignments

    def iter_groups_by_assignment(self):
        """
        Returns an iterator over all :class:`.GroupList` objects for this student.
        Shortcut for ``self.assignments.itervalues()``.
        """
        return self.assignments.itervalues()

    def add_group(self, group):
        """
        Used by :class:`.GroupsGroupedByRelatedStudentAndAssignment` to add groups.
        """
        self.assignments[group.parentnode_id].append(group)

    def prettyprint(self):
        """
        Prettyprint for debugging.
        """
        print '{0}:'.format(self.user)
        for assignmentid, groups in self.assignments.iteritems():
            print '  - Assignment ID: {0}'.format(assignmentid)
            for group in groups:
                if group.feedback:
                    grade = '{0} (points:{1},passed:{2})'.format(group.feedback.grade,
                        group.feedback.points, group.feedback.is_passing_grade)
                else:
                    grade = None
                print '    - {0}: {1}'.format(group, grade)

    def __str__(self):
        """
        Returns a short representation of the object that should be useful when debugging.
        """
        return u'AggreatedRelatedStudentInfo(user={0}, assignmentcount={1}, grades={2!r})'.format(
            self.user.username,
            len(self.assignments),
            [str(gradelist.get_best_gradestring()) for gradelist in self.iter_groups_by_assignment()]
        )


class GroupsGroupedByRelatedStudentAndAssignment(object):
    """
    Provides an easy-to-use API for overviews over the results of all students
    in a period.

    Typical usage (create a csv of the period)::

        grouper = GroupsGroupedByRelatedStudentAndAssignment(self.testhelper.sub_p1)

        header = ['USER','IGNORED']
        for assignment in grouper.iter_assignments():
            header.append(assignment.short_name)
        print ';'.join(header)

        def print_aggregated_relstudentinfo(aggregated_relstudentinfo, ignored):
            user = aggregated_relstudentinfo.user
            row = [user.username, ignored]
            for grouplist in aggregated_relstudentinfo.iter_groups_by_assignment():
                # NOTE: There can be more than one group if the same student is in more than one
                #       group on an assignment - we select the "best" feedback.
                feedback = grouplist.get_feedback_with_most_points()
                if feedback:
                    row.append(feedback.grade)
                else:
                    row.append('NO-FEEDBACK')
            print ';'.join(row)

        # Print all related students
        for aggregated_relstudentinfo in grouper.iter_relatedstudents_with_results():
            print_aggregated_relstudentinfo(aggregated_relstudentinfo, 'NO')

        # Last we print the ignored students (non-related students that are in a group)
        for aggregated_relstudentinfo in grouper.iter_students_with_feedback_that_is_candidate_but_not_in_related():
            print_aggregated_relstudentinfo(aggregated_relstudentinfo, 'YES')
    """
    def __init__(self, period, order_assignments_by='publishing_time'):
        self.period = period
        self.order_assignments_by = order_assignments_by
        self._collect_assignments()
        self._initialize_result()
        self._add_groups_to_result()

    def _collect_assignments(self):
        self.assignments = []
        for assignment in self.period.assignments.all().order_by(self.order_assignments_by):
            self.assignments.append(assignment)

    def _create_assignmentsdict(self):
        dct = OrderedDict()
        for assignment in self.assignments:
            dct[assignment.id] = GroupList()
        return dct

    def _initialize_result(self):
        self.result = {}
        for relatedstudent in self.period.relatedstudent_set.all():
            self.result[relatedstudent.user_id] = AggreatedRelatedStudentInfo(
                user = relatedstudent.user,
                assignments = self._create_assignmentsdict()
            )

    def _create_or_add_ignoredgroup(self, ignoreddict, candidate):
        if not candidate.student_id in ignoreddict:
            ignoreddict[candidate.student_id] = AggreatedRelatedStudentInfo(
                user = candidate.student,
                assignments = self._create_assignmentsdict()
            )
        return ignoreddict[candidate.student_id]

    def _add_groups_to_result(self):
        groupqry = AssignmentGroup.objects.filter(parentnode__parentnode=self.period)
        groupqry = groupqry.select_related('parentnode', 'parentnode__parentnode')
        self.ignored_students = {}
        self.ignored_students_with_results = {}
        for group in groupqry:
            for candidate in group.candidates.all():
                if candidate.student_id in self.result:
                    self.result[candidate.student_id].add_group(group)
                else:
                    self._create_or_add_ignoredgroup(self.ignored_students, candidate).add_group(group)
                    if group.feedback:
                        self._create_or_add_ignoredgroup(self.ignored_students_with_results, candidate).add_group(group)

    def iter_assignments(self):
        """
        Iterate over all the assignments, yielding Assignment-objects. The objects
        are iterated in the order specified by the ``order_assignments_by`` argument
        for ``__init__``.
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
        return self.result.itervalues()

    def iter_students_that_is_candidate_but_not_in_related(self):
        """
        Iterate over the students that is candidate on one or more groups, but not registered as
        related students.
        """
        return self.ignored_students.itervalues()

    def iter_students_with_feedback_that_is_candidate_but_not_in_related(self):
        """
        Same as :meth:`.iter_students_that_is_candidate_but_not_in_related`, but it does not include
        the students that have no feedback.
        """
        return self.ignored_students_with_results.itervalues()
