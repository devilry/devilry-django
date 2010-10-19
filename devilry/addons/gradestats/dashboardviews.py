from django.template.loader import render_to_string
from django.template import RequestContext

from devilry.core.models import Period
from devilry.core.utils.GroupNodes import group_nodes


class GroupPeriodsBySubject(object):
    def __init__(self, periods):
        self.periods = periods

    def __iter__(self):
        def iterate(it, cur):
            yield cur

        it = self.periods.__iter__()
        cur = it.next()
        current_subject = cur.parentnode
        periods = []
        while True:
            if cur.parentnode.id == current_subject.id:
                periods.append(cur)
            else:
                yield current_subject, periods
                current_subject = cur.parentnode
                periods = [cur]
            cur = it.next()



def overview(request):
    order = ('parentnode__short_name', '-start_time')
    where_is_admin_or_superadmin = Period.where_is_admin_or_superadmin(
            request.user).order_by(*order)
    where_is_student = Period.objects.filter(
            assignments__assignmentgroups__candidates__student=request.user)
    where_is_student = where_is_student.distinct().order_by(*order)
    studcount = where_is_student.count()
    admcount = where_is_admin_or_superadmin.count()
    if studcount == 0 and admcount == 0:
        return None


    adm = group_nodes(where_is_admin_or_superadmin, 0)
    stud = group_nodes(where_is_student, 0)

    return render_to_string(
        'devilry/gradestats/overview.django.html', {
            'showboth': studcount and admcount,
            'where_is_admin_or_superadmin': adm,
            'where_is_student': stud,
        }, context_instance=RequestContext(request))
