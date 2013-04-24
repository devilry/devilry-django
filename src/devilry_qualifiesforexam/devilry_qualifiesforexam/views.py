from django.utils.translation import ugettext as _
from extjs4.views import Extjs4AppView
from django.views.generic import TemplateView
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden

from devilry.apps.core.models import Period
from devilry_qualifiesforexam.models import Status


class AppView(Extjs4AppView):
    template_name = "devilry_qualifiesforexam/app.django.html"
    appname = 'devilry_qualifiesforexam'
    title = _('Devilry - Qualifies for final exam')


class StatusPrintView(TemplateView):
    template_name = 'devilry_qualifiesforexam/statusprint.django.html'

    def get(self, request, status_id):
        try:
            self.status = Status.objects.get(pk=status_id)
        except Status.DoesNotExist:
            return HttpResponseNotFound()
        else:
            if not Period.where_is_admin_or_superadmin(self.request.user).filter(id=self.status.period_id).exists():
                return HttpResponseForbidden()
            elif self.status.status != Status.READY:
                return HttpResponseNotFound()
            else:
                return super(StatusPrintView, self).get(request, status_id)


    def get_context_data(self, **kwargs):
            context = super(StatusPrintView, self).get_context_data(**kwargs)
            return context
