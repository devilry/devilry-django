from django.db.models import Q
from djangorestframework.views import View
from djangorestframework.permissions import IsAuthenticated

from devilry.apps.core.models import Assignment


def format_datetime(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')


class AllWhereIsAdmin(View):
    """
    All subjects, periods and assignments where the authenticated user is admin.
    """
    permissions = (IsAuthenticated,)

    def _assignments_where_is_admin(self):
        user = self.request.user
        qry = Assignment.objects.filter(Q(admins=user) |
                                        Q(parentnode__admins=user) |
                                        Q(parentnode__parentnode__admins=user))
        qry = qry.select_related('parentnode', 'parentnode__parentnode')
        qry = qry.prefetch_related('parentnode__admins', 'parentnode__parentnode__admins')
        qry = qry.order_by('-publishing_time')
        return qry

    def _subject_to_dict(self, subject):
        return {'id': subject.id,
                'short_name': subject.short_name,
                'long_name': subject.long_name,
                'periods': {}}

    def _period_to_dict(self, period):
        return {'id': period.id,
                'short_name': period.short_name,
                'long_name': period.long_name,
                'start_time': format_datetime(period.start_time),
                'assignments': []}

    def _assignment_to_dict(self, assignment):
        return {'id': assignment.id,
                'short_name': assignment.short_name,
                'long_name': assignment.long_name,
                'publishing_time': format_datetime(assignment.publishing_time)}


    def _aggregate_data(self):
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
        subjectsAggr = self._aggregate_data()
        subjectsAggr = self._sort_aggregated_data(subjectsAggr)
        return subjectsAggr
