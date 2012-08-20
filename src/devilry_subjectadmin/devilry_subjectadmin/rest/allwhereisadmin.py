from datetime import datetime
from django.db.models import Q, Count
from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Assignment
from devilry.apps.core.models import Period
from devilry.apps.core.models import Subject


def format_datetime(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')


class AllWhereIsAdmin(View):
    """
    All subjects, periods and assignments where the authenticated user is admin.

    **NOTE:** This API only works for subject admins, since it does not
    recursively check for permissions on parentnodes, only up to subject.

    # GET

    ## Parameters
    Use the ``only_active=yes`` parameter in the querystring to only list active periods.

    ## Returns
    A list of subjects where each subject contains a list of periods, and each
    period contains a list of assignments. In addition to the regular metadata,
    each item has two special attributes:

    - ``is_admin``: Is admin on this item (not inherited, but exactly on the item).
    - ``can_administer``: Is admin on this item or any parent.
    """
    permissions = (IsAuthenticated,)

    def _assignments_where_is_admin(self):
        user = self.request.user
        qry = Assignment.objects.filter(Q(admins=user) |
                                        Q(parentnode__admins=user) |
                                        Q(parentnode__parentnode__admins=user))
        qry = qry.select_related('parentnode', 'parentnode__parentnode')
        qry = qry.prefetch_related('admins', 'parentnode__admins', 'parentnode__parentnode__admins')
        qry = qry.order_by('-publishing_time')
        if self.only_active:
            now = datetime.now()
            qry = qry.filter(Q(parentnode__start_time__lte=now) & Q(parentnode__end_time__gte=now))
        return qry

    def _is_admin(self, basenode):
        return self.request.user in basenode.admins.all()

    def _subject_to_dict(self, subject):
        is_admin = self._is_admin(subject)
        return {'id': subject.id,
                'short_name': subject.short_name,
                'long_name': subject.long_name,
                'is_admin': is_admin,
                'can_administer': is_admin,
                'periods': {}}

    def _period_to_dict(self, period):
        is_admin = self._is_admin(period)
        return {'id': period.id,
                'short_name': period.short_name,
                'long_name': period.long_name,
                'start_time': format_datetime(period.start_time),
                'is_admin': is_admin,
                'can_administer': is_admin or self._is_admin(period.parentnode),
                'assignments': []}

    def _assignment_to_dict(self, assignment):
        is_admin = self._is_admin(assignment)
        return {'id': assignment.id,
                'short_name': assignment.short_name,
                'long_name': assignment.long_name,
                'is_admin': is_admin,
                'can_administer': is_admin or self._is_admin(assignment.parentnode) or self._is_admin(assignment.parentnode.parentnode),
                'publishing_time': format_datetime(assignment.publishing_time)}


    def _aggregate_data_from_assignmentqry(self):
        assignments = self._assignments_where_is_admin()
        subjectsAggr = {}
        for assignment in assignments:

            subject = assignment.parentnode.parentnode
            if not subject.short_name in subjectsAggr:
                subjectsAggr[subject.short_name] = self._subject_to_dict(subject)
            subjectDict = subjectsAggr[subject.short_name]

            period = assignment.parentnode
            if not period.short_name in subjectDict['periods']:
                subjectDict['periods'][period.short_name] = self._period_to_dict(period)
            periodDict = subjectDict['periods'][period.short_name]

            periodDict['assignments'].append(self._assignment_to_dict(assignment))
        return subjectsAggr


    #
    # Empty periods and subjects
    #
    def _subjects_without_periods(self):
        qry = Subject.objects.filter(admins=self.request.user)
        qry = qry.prefetch_related('admins')
        qry = qry.annotate(number_of_periods=Count('periods'))
        qry = qry.filter(number_of_periods=0)
        return qry

    def _add_subjects_without_periods(self, subjectsAggr):
        if self.only_active:
            # NOTE: Empty subjects can not have an active period, so they should not be included
            return subjectsAggr
        for subject in self._subjects_without_periods():
            subjectsAggr[subject.short_name] = self._subject_to_dict(subject)
        return subjectsAggr

    def _periods_without_assignments(self):
        user = self.request.user
        qry = Period.objects.filter(Q(admins=user) |
                                    Q(parentnode__admins=user))
        qry = qry.prefetch_related('admins', 'parentnode__admins')
        qry = qry.annotate(number_of_assignments=Count('assignments'))
        qry = qry.filter(number_of_assignments=0)
        if self.only_active:
            now = datetime.now()
            qry = qry.filter(Q(start_time__lte=now) & Q(end_time__gte=now))
        return qry

    def _add_periods_without_assignments(self, subjectsAggr):
        for period in self._periods_without_assignments():
            subject = period.parentnode
            if not subject.short_name in subjectsAggr:
                subjectsAggr[subject.short_name] = self._subject_to_dict(subject)
            subjectDict = subjectsAggr[subject.short_name]
            subjectDict['periods'][period.short_name] = self._period_to_dict(period)
        return subjectsAggr

    #
    # Sorting
    #

    def _period_sorter(self, a, b):
        return cmp(b['start_time'], a['start_time'])

    def _subject_sorter(self, a, b):
        return cmp(a['long_name'], b['long_name'])

    def _sort_aggregated_data(self, subjectsAggr):
        for subject_shortname, subjectDict in subjectsAggr.iteritems():
            subjectDict['periods'] = subjectDict['periods'].values()
            subjectDict['periods'].sort(self._period_sorter)
        subjectsAggr = subjectsAggr.values()
        subjectsAggr.sort(self._subject_sorter)
        return subjectsAggr

    def get(self, request):
        self.only_active = request.GET.get('only_active') == 'yes'
        subjectsAggr = self._aggregate_data_from_assignmentqry()
        subjectsAggr = self._add_subjects_without_periods(subjectsAggr)
        subjectsAggr = self._add_periods_without_assignments(subjectsAggr)
        subjectsAggr = self._sort_aggregated_data(subjectsAggr)
        return subjectsAggr
