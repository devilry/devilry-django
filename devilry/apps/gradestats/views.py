from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseForbidden
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.db.models.query import QuerySet
from django.template.defaultfilters import floatformat
from django.http import HttpResponse

from ..core.models import AssignmentGroup, Period
#from ..core import pluginloader
from ..ui.filtertable import (FilterTable, Columns, Col, Row,
        RowAction, Filter, FilterLabel)
from ..core.utils.coreutils import AssignmentUtils

#pluginloader.autodiscover()


def _get_periodstats(period, user):
    groups = AssignmentGroup.published_where_is_candidate(user).filter(
            parentnode__parentnode=period)
    s = sum([g.scaled_points for g in groups])
    maxpoints = sum([g.parentnode.pointscale for g in groups])
    return s, maxpoints, groups

@login_required
def userstats(request, period_id):
    period = get_object_or_404(Period, pk=period_id)
    total, maxpoints, groups = _get_periodstats(period, request.user)
    show_sum = not any(not g.parentnode.students_can_see_points for g in groups)
    return render_to_response(
        'devilry/gradestats/user.django.html', {
            'period': period,
            'userobj': request.user,
            'total': total,
            'maxpoints': maxpoints,
            'groups': groups,
            'show_sum': show_sum,
        }, context_instance=RequestContext(request))


@login_required
def admin_userstats(request, period_id, username):
    period = get_object_or_404(Period, pk=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")
    user = get_object_or_404(User, username=username)
    total, maxpoints, groups = _get_periodstats(period, user)
    return render_to_response(
        'devilry/gradestats/admin-user.django.html', {
            'period': period,
            'userobj': user,
            'total': total,
            'maxpoints': maxpoints,
            'groups': groups,
        }, context_instance=RequestContext(request))


class FilterPeriodPassed(Filter):
    def get_labels(self, properties):
        return [FilterLabel(_("All")),
                FilterLabel(_("Yes"),
                    _("This takes a long time to calculate on big datasets.")),
                FilterLabel(_("No"),
                    _("This takes a long time to calculate on big datasets."))]

    def filter(self, properties, dataset, selected):
        choice = selected[0]
        if choice == 0:
            return dataset

        period = properties['period']
        if choice == 1:
            #print [period for user in dataset]
            return [user for user in dataset if
                    period.student_passes_period(user)]
        elif choice == 2:
            return [user for user in dataset if
                    not period.student_passes_period(user)]



class PeriodStatsFilterTable(FilterTable):
    id = 'gradestats-period-filtertable'
    use_rowactions = True
    search_help = _('Search for any part of the username')
    resultcount_supported = False
    default_order_by = "username"
    has_related_actions = False
    has_selection_actions = False
    default_perpage = 10

    filters = [FilterPeriodPassed(_("Passing grade?"))]

    def __init__(self, request, period):
        self.period = period
        self.assignments_in_period = period.assignments.all().order_by(
                "publishing_time")
        self.maxpoints = sum([a.pointscale for a in self.assignments_in_period])
        super(PeriodStatsFilterTable, self).__init__(request)
        self.set_properties(period=period)

    def get_columns(self):
        cols = Columns()
        cols.add(Col("username", "Username", can_order=True))
        cols.add(Col("sumperiod", "Sum period", can_order=True,
            title=_("The sum of points on all assignments in this period.")))
        cols.add(Col("sumvisible", "Sum visible", can_order=False,
            title=_("The sum of points on the visible assignments.")))
        for assignment in self.assignments_in_period:
            title = AssignmentUtils.tooltip_html(assignment)
            cols.add(
                Col(assignment.id,
                    "%s (%s)" % (assignment.short_name, assignment.pointscale),
                    can_order=True, optional=True, active_default=True,
                    title=title))
        return cols

    def search(self, dataset, qry):
        return dataset.filter(username__contains=qry)

    def format_active_optional_columns(self, active_optional_columns):
        cols = [int(x) for x in active_optional_columns]
        visible_assignments_in_period = self.assignments_in_period.filter(
                id__in=cols)
        return (visible_assignments_in_period, cols)


    @classmethod
    def iter_selected_assignments(cls, period, user,
            visible_assignments):
        """
        Iterate over the curretly visible assignments in a period.

        :param period: The current :class:`devilry.core.models.Period`.
        :param user: A django user object.
        :param visible_assignments: A QuerySet matching the currently
            visible assignments.
        :return:
            A iterator yielding the (scaled_points, is_passing_grade, status)
            on all ``visible_assignments`` where the current user is in a
            group, and (None, None, None) on assignments ``visible_assignments``
            where the current user is not in a group.
        """
        groups = AssignmentGroup.where_is_candidate(user).filter(
                parentnode__parentnode=period,
                parentnode__in=visible_assignments)
        groups = groups.values_list(
                        "parentnode__id", "scaled_points",
                        "is_passing_grade", "status")

        it = groups.__iter__()
        def itnext():
            try:
                return it.next()
            except StopIteration:
                return None, None, None, None

        id, scaled_points, is_passing_grade, status = itnext()
        for group in visible_assignments:
            if id == group.id:
                yield scaled_points, is_passing_grade, status
                id, scaled_points, is_passing_grade, status = itnext()
            else:
                yield None, None, None


    def create_row(self, user, active_optional_columns):
        row = Row(user.username, title=user.username)
        row.add_actions(
            RowAction("details",
                reverse('devilry-gradestats-admin_userstats',
                    args=[str(self.period.id), str(user.username)]))
        )
        visible_assignments, visible_assignmentids = active_optional_columns

        row.add_cell(user.username)
        row.add_cell(floatformat(user.sumperiod))
        row.add_cell("") # total visible points (inserted below)

        total = 0
        for group in self.__class__.iter_selected_assignments(
                self.period, user, visible_assignments):
            scaled_points, is_passing_grade, status = group
            if scaled_points == None:
                row.add_cell("")
            else:
                row.add_cell(floatformat(scaled_points),
                        cssclass=AssignmentGroup.status_mapping_cssclass[status])
                total += scaled_points
        row[2].value = floatformat(total)
        return row


    def create_dataset(self):
        dataset = User.objects.filter(
            candidate__assignment_group__parentnode__parentnode=self.period).distinct()
        dataset = dataset.annotate(
                sumperiod=Sum('candidate__assignment_group__scaled_points'))
        total = dataset.count()
        return total, dataset

    def order_by(self, dataset, colid, order_asc, qryprefix):
        if colid == 'username' or colid == 'sumperiod':
            if isinstance(dataset, QuerySet):
                return dataset.order_by(qryprefix + colid)
            else:
                # If a filter (FilterPeriodPassed) returns a list...
                f = lambda a,b: cmp(getattr(a, colid), getattr(b,colid))
                dataset.sort(cmp=f)
                if order_asc:
                    dataset.reverse()
                return dataset

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
        result = [
                kv[u.username] for u in users_by_points \
                if u.username in kv]
        print result
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
    return render_to_response('devilry/gradestats/periodstats.django.html', {
        'filtertbl': tbl,
        'period': period
        }, context_instance=RequestContext(request))




def _qry_all_users_in_period(period, assignments):
    dataset = User.objects.filter(
        candidate__assignment_group__parentnode__parentnode=period).distinct()
    dataset = dataset.annotate(
            sumperiod=Sum('candidate__assignment_group__scaled_points'))
    for user in dataset:
        l = []
        l.append(user.username)
        l.append(floatformat(user.sumperiod))

        for group in PeriodStatsFilterTable.iter_selected_assignments(
                period, user, assignments):
            scaled_points, is_passing_grade, status = group
            if scaled_points == None:
                l.append("")
            else:
                l.append(floatformat(scaled_points))
        yield user, l



@login_required
def periodstats_csv(request, period_id):
    period = get_object_or_404(Period, id=period_id)
    if not period.can_save(request.user):
        return HttpResponseForbidden("Forbidden")

    assignments = period.assignments.all().order_by("publishing_time")
    csv = "\n".join([",".join(userdata) \
            for user, userdata in _qry_all_users_in_period(period,
                assignments)])
    csv = "username,sum,%s\n%s" % (",".join([a.short_name for a in assignments]), csv)
    response = HttpResponse(csv, mimetype="text/plain")
    filename = "%s.csv" % period.get_path()
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response
