from devilry.apps.core.models import Candidate
from devilry.apps.core.models import StaticFeedback
from devilry.apps.core.models import deliverytypes



class NotInPrevious(Exception):
    pass
class OnlyFailingInPrevious(Exception):
    pass
class HasFeedback(Exception):
    pass

class PassingGradeOnlyInMultiCandidateGroups(Exception):
    def __init__(self, groups):
        self.groups = groups
        super(PassingGradeOnlyInMultiCandidateGroups, self).__init__()

class NotExactlyOneCandidateInGroup(Exception):
    def __init__(self, candidatecount):
        self.candidatecount = candidatecount
        super(NotExactlyOneCandidateInGroup, self).__init__()


class MarkAsPassedInPreviousPeriod(object):

    def __init__(self, assignment):
        self.assignment = assignment

    def _get_previous_periods(self):
        period = self.assignment.parentnode
        subject = period.parentnode
        qry = subject.periods.filter(start_time__lt=period.start_time)
        qry = qry.order_by('-start_time') # Order descending, so we find the newest feedback when looping
        return [period for period in qry]

    def get_previous_periods(self):
        """
        Get the previous periods within the subject of the ``assignment``.
        """
        if not hasattr(self, '_previous_periods'):
            self._previous_periods = self._get_previous_periods()
        return self._previous_periods

    def mark_all(self, pretend=False):
        """
        Mark all groups in assignment. Ignores:

            - Ignores groups with no candidates.
            - Ignores groups on this assignment with more than one candidate.
              The group from a previous period (the alias) may have multiple
              candidates.

        Collects the results in a dict with the following keys:

        - ``marked``: List of marked group pairs (group, oldgroup), where
          ``group`` is the group from the current assignment.
        - ``ignored``: Ignored groups organized by the reason for the ignore (dict):
            - ``multiple_students_groups``
            - ``no_students_in_group``
            - ``not_in_previous``
            - ``only_failing_grade_in_previous``
            - ``only_multicandidategroups_passed``: The group only matches old groups where there are more than one candidate with passing grade.
            - ``has_feedback``: The group already has feedback.
        """
        ignored = {'multiple_students_groups': [],
                   'no_students_in_group': [],
                   'not_in_previous': [],
                   'only_failing_grade_in_previous': [],
                   'only_multicandidategroups_passed': [],
                   'has_feedback': []}
        marked = []

        for group in self.assignment.assignmentgroups.all():
            candidates = group.candidates.all()
            if len(candidates) == 0:
                ignored['no_students_in_group'].append(group)
            elif len(candidates) == 1:
                try:
                    if pretend:
                        oldgroup = self.find_previously_passed_group(group)
                    else:
                        oldgroup = self.mark_group(group)
                except OnlyFailingInPrevious:
                    ignored['only_failing_grade_in_previous'].append(group)
                except NotInPrevious:
                    ignored['not_in_previous'].append(group)
                except PassingGradeOnlyInMultiCandidateGroups:
                    ignored['only_multicandidategroups_passed'].append(group)
                except HasFeedback:
                    ignored['has_feedback'].append(group)
                else:
                    marked.append((group, oldgroup))
            else:
                ignored['multiple_students_in_group'].append(group)
        return {'marked': marked,
                'ignored': ignored}

    def mark_group(self, group):
        oldgroup = self.find_previously_passed_group(group)
        self._mark_as_delivered_in_previous(group, oldgroup)
        return oldgroup

    def find_previously_passed_group(self, group):
        """
        Find the newest delivery with passing feedback for this group with
        assignment matching ``self.assignment``.
        """
        candidates = group.candidates.all()
        if len(candidates) != 1:
            raise NotExactlyOneCandidateInGroup(len(candidates))
        candidate = candidates[0]

        if StaticFeedback.objects.filter(delivery__deadline__assignment_group=group).exists():
            raise HasFeedback()

        candidates_from_previous = self._find_candidates_in_previous(candidate)
        if candidates_from_previous:
            passing_but_multigroup = []
            for candidate in candidates_from_previous:
                oldgroup = candidate.assignment_group
                if oldgroup.feedback and oldgroup.feedback.is_passing_grade \
                        and not oldgroup.feedback.delivery.delivery_type == deliverytypes.ALIAS:
                    if oldgroup.candidates.count() != 1:
                        passing_but_multigroup.append(oldgroup)
                    else:
                        return oldgroup
            if passing_but_multigroup:
                raise PassingGradeOnlyInMultiCandidateGroups(passing_but_multigroup)
            raise OnlyFailingInPrevious()
        else:
            raise NotInPrevious()

    def _mark_as_delivered_in_previous(self, group, oldgroup):
        latest_deadline = group.deadlines.order_by('-deadline')[0]
        oldfeedback = oldgroup.feedback
        delivery = latest_deadline.deliveries.create(successful=True,
                                                     delivery_type=deliverytypes.ALIAS,
                                                     alias_delivery=oldfeedback.delivery)
        delivery.feedbacks.create(grade=oldfeedback.grade,
                                  is_passing_grade=oldfeedback.is_passing_grade,
                                  points=oldfeedback.points,
                                  rendered_view=oldfeedback.rendered_view,
                                  saved_by=oldfeedback.saved_by)

    def _find_candidates_in_previous(self, candidate):
        matches = []
        for period in self.get_previous_periods():
            try:
                previous_candidate = Candidate.objects.get(assignment_group__parentnode__parentnode=period,
                                                           assignment_group__parentnode__short_name=self.assignment.short_name,
                                                           student=candidate.student)
            except Candidate.DoesNotExist:
                pass
            else:
                matches.append(previous_candidate)
        return matches
