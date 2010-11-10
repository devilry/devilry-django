from datetime import datetime
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Max

from devilry.core.models import AssignmentGroup

from utils import filter_not_corrected



class ExaminerImportantItem(object):
    sessionid = None

    def __init__(self, request):
        self.request = request
        self.savesession = False
        self.sessionprefix = "dashboard_examiner_" + self.sessionid + "_"
        self.groups, self.total = self.filter()
        if self.savesession:
            self.request.session.save()

    def _querystring_to_sessionbool(self, s):
        value = self.request.GET.get(s)
        if value:
            v = value == "yes"
            self.request.session[s] = v
            self.savesession = True
            return v
        return self.request.session.get(s, False)

    def _handle_buttons(self, groups):
        orderdesc = self._querystring_to_sessionbool(
                self.sessionprefix + "orderdesc")
        orderprefix = ""
        if orderdesc:
            orderprefix = "-"
        groups = groups.order_by(
                orderprefix + 'time_of_last_delivery')
        showall = self._querystring_to_sessionbool(
                self.sessionprefix + "showall")
        if not showall:
            groups = groups[:3]
        return groups

    def __len__(self):
        return self.total

    def render(self, request):
        from devilry.core.utils.GroupNodes import group_nodes
        assignments = group_nodes(self.groups, 0)
        return render_to_string(
            "devilry/examiner/dashboard/%s.django.html" % self.sessionid, {
                "assignments": assignments,
                "total": self.total,
                "groupcount": self.groups.count()
            }, context_instance=RequestContext(request))


class NotCorrected(ExaminerImportantItem):
    sessionid = "not_corrected"
    def filter(self):
        not_corrected = filter_not_corrected(self.request.user)
        not_corrected_count = not_corrected.count()
        not_corrected = self._handle_buttons(not_corrected)
        return not_corrected, not_corrected_count

class NotPublished(ExaminerImportantItem):
    sessionid = "not_published"
    def filter(self):
        groups = AssignmentGroup.active_where_is_examiner(self.request.user)
        not_published = groups.filter(
                is_open=True,
                status=AssignmentGroup.CORRECTED_NOT_PUBLISHED)
        not_published = not_published.annotate(
                active_deadline=Max('deadlines__deadline'),
                time_of_last_delivery=Max('deliveries__time_of_delivery'),
                time_of_last_feedback=Max('deliveries__feedback__last_modified'))
        not_published = not_published.order_by('-time_of_last_feedback')
        not_published_count = not_published.count()
        not_published = self._handle_buttons(not_published)
        return not_published, not_published_count


def examiner_important(request, *args, **kwargs):
    not_corrected = NotCorrected(request)
    not_published = NotPublished(request)
    if len(not_corrected) == 0 and len(not_published) == 0:
        return None

    print
    print "#################################"
    print not_corrected.groups
    print "#################################"
    print
    return render_to_string(
        'devilry/examiner/dashboard/examiner_important.django.html', {
            "items": [
                not_corrected.render(request),
                not_published.render(request)]
        }, context_instance=RequestContext(request))
