from datetime import datetime
from django.template.loader import render_to_string
from django.template import RequestContext
from django.db.models import Max

from devilry.core.models import AssignmentGroup

from utils import filter_not_corrected




class ExaminerImportant(object):
    sessionprefix = "dashboard_examiner"
    def __init__(self, request):
        self.request = request
        self.now = datetime.now()
        self.groups = AssignmentGroup.active_where_is_examiner(request.user)
        self.savesession = False
        self._not_corrected()
        self._not_published()

    def querystring_to_sessionbool(self, s):
        value = self.request.GET.get(s)
        if value:
            v = value == "yes"
            self.request.session[s] = v
            self.savesession = True
            return v
        return False

    def _not_corrected(self):
        sp = self.sessionprefix + "_not_corrected_"
        not_corrected = self.groups.filter(
                is_open=True,
                status=1)
        not_corrected = not_corrected.annotate(
                active_deadline=Max('deadlines__deadline'),
                time_of_last_delivery=Max('deliveries__time_of_delivery'))
        not_corrected = not_corrected.filter(
                active_deadline__lt=self.now)
        self.not_corrected_count = not_corrected.count()
        #not_corrected = not_corrected.distinct("parentnode")

        orderdesc = self.querystring_to_sessionbool(sp + "orderdesc")
        orderprefix = ""
        if orderdesc:
            orderprefix = "-"
        not_corrected = not_corrected.order_by(
                orderprefix + 'time_of_last_delivery')

        showall = self.querystring_to_sessionbool(sp + "showall")
        if not showall:
            not_corrected = not_corrected[:3]
        self.not_corrected = not_corrected

    def _not_published(self):
        not_published = self.groups.filter(
                is_open=True,
                status=2)
        not_published = not_published.annotate(
                active_deadline=Max('deadlines__deadline'),
                time_of_last_delivery=Max('deliveries__time_of_delivery'),
                time_of_last_feedback=Max('deliveries__feedback__last_modified'))
        not_published = not_published.order_by('-time_of_last_feedback')
        self.not_published_count = not_published.count()
        not_published = not_published[:3]
        self.not_published = not_published

    def response(self):
        if self.not_corrected_count == 0 and self.not_published_count == 0:
            return None
        if self.savesession:
            self.request.session.save()
        return render_to_string(
            'devilry/examiner/dashboard/examiner_important.django.html', {
                'not_corrected_count': self.not_corrected_count,
                'not_corrected': self.not_corrected,
                'not_published_count': self.not_published_count,
                'not_published': self.not_published,
                }, context_instance=RequestContext(self.request))

def examiner_important(request, *args, **kwargs):
    return ExaminerImportant(request).response()
