from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Sum

from devilry.core.models import AssignmentGroup, Period
from devilry.core import pluginloader
from devilry.ui.filtertable import FilterTable, Columns, Col, Row

pluginloader.autodiscover()


def _get_periodstats(period, user):
    groups = AssignmentGroup.published_where_is_candidate(user).filter(
            parentnode__parentnode=period)
    s = sum([g.scaled_points for g in groups])
    return s, groups

@login_required
def userstats(request, period_id):
    period = get_object_or_404(Period, pk=period_id)
    total, groups = _get_periodstats(period, request.user)
    return render_to_response(
        'devilry/gradestats/user.django.html', {
            'period': period,
            'userobj': request.user,
            'total': total,
            'groups': groups,
        }, context_instance=RequestContext(request))


@login_required
def admin_userstats(request, period_id, username):
    period = get_object_or_404(Period, pk=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    user = get_object_or_404(User, username=username)
    total, groups = _get_periodstats(period, user)
    return render_to_response(
        'devilry/gradestats/admin-user.django.html', {
            'period': period,
            'userobj': user,
            'total': total,
            'groups': groups,
        }, context_instance=RequestContext(request))



class PeriodStatsFilterTable(FilterTable):
    id = 'gradestats-period-filtertable'

    def __init__(self, request, period):
        self.period = period
        self.assignments_in_period = period.assignments.all()
        self.maxpoints = sum([a.pointscale for a in self.assignments_in_period])
        super(PeriodStatsFilterTable, self).__init__(request)

    def get_columns(self):
        cols = Columns()
        cols.add(Col("username", "Username", can_order=True))
        cols.add(Col("sumpoints", "Sum", can_order=True))
        for assignment in self.assignments_in_period:
            cols.add(Col(assignment.id, assignment.short_name,
                can_order=True))
        return cols

    def create_row(self, user, active_optional_cols):
        row = Row(user.username, title=user.username)

        assignments = AssignmentGroup.where_is_candidate(user).filter(
                parentnode__parentnode=self.period).values_list(
                        "scaled_points", "is_passing_grade")
        if len(self.assignments_in_period) > len(assignments):
            # Handle user in multiple groups on the same assignment by
            # showing their points as 0. How to calculate points when a user
            # is in multiple groups has not been resolved yet, and might
            # never be supported.
            assignments = [(0, False) for a in self.assignments_in_period]
                
        row.add_cell(user.username)
        row.add_cell(user.sumpoints)
        for scaled_points, is_passing_grade in assignments:
            row.add_cell(scaled_points)
        return row

    def create_dataset(self):
        dataset = User.objects.filter(
            candidate__assignment_group__parentnode__parentnode=self.period).distinct()
        dataset = dataset.annotate(
                sumpoints=Sum('candidate__assignment_group__scaled_points'))
        total = dataset.count()
        return total, dataset

    def order_by(self, dataset, colid, order_asc, qryprefix):
        if colid == 'username' or colid == 'sumpoints':
            return dataset.order_by(qryprefix + colid)

        # A bit of a hack to sort assignment by scaled points..
        # 1. Get all users on the assignment ordered by their scaled points.
        # 2. Create a dict of the current dataset with username as key, for
        #    fast lookup of the "real" data (the data from #1 is only from
        #    the assignment, not from the entire period).
        # 3. Create a list from the original dataset ordered as the list
        #    from #1.
        # This works because the dataset only has to be a iterable
        # supporting slicing.
        assignment_id = int(colid)
        users_by_points = User.objects.filter(
            candidate__assignment_group__parentnode=assignment_id).distinct()
        users_by_points = users_by_points.order_by(
                qryprefix + 'candidate__assignment_group__scaled_points')
        kv = dict([(u.username, u) for u in dataset])
        result = [kv.get(u.username,0) for u in users_by_points]
        return result



@login_required
def periodstats_json(request, period_id):
    period = get_object_or_404(Period, id=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    tbl = PeriodStatsFilterTable(request, period)
    return tbl.json_response()

@login_required
def periodstats(request, period_id):
    period = get_object_or_404(Period, id=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    tbl = PeriodStatsFilterTable.initial_html(request,
            reverse('devilry-gradestats-periodstats_json',
                args=[str(period_id)]))
    return render_to_response('devilry/admin/list-nodes-generic.django.html', {
        'title': "Period stats",
        'filtertbl': tbl
        }, context_instance=RequestContext(request))
