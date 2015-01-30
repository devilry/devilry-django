# from django.utils.translation import ugettext_lazy as _
from datetime import datetime

from django.template import defaultfilters
from django.views.generic import DetailView, TemplateView
from django_cradmin.viewhelpers import objecttable
from crispy_forms import layout
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django_cradmin import crapp
from django_cradmin.apps.cradmin_temporaryfileuploadstore.crispylayouts import BulkFileUploadSubmit
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection, TemporaryFile
from django_cradmin.apps.cradmin_temporaryfileuploadstore.widgets import BulkFileUploadWidget
from django_cradmin.viewhelpers import formbase

from devilry.apps.core.models import Assignment, Candidate, Delivery, FileMeta


# DEFAULT_DEADLINE_EXPIRED_MESSAGE = _(
#     'Your active deadline, %(deadline)s has expired, and the administrators of %(assignment)s '
#     'have configured HARD deadlines. This means that you can not add more deliveries to this '
#     'assignment unless an administrator extends your deadline.')
# DEADLINE_EXPIRED_MESSAGE = getattr(settings, 'DEVILRY_DEADLINE_EXPIRED_MESSAGE', DEFAULT_DEADLINE_EXPIRED_MESSAGE)
from devilry.devilry_student.cradmin_group.utils import check_if_last_deadline_has_expired

DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES = getattr(settings, 'DELIVERY_DELIVERY_TEMPFILES_TIME_TO_LIVE_MINUTES', 120)


class Overview(TemplateView):
    template_name = 'devilry_student/cradmin_group/deliveriesapp/delivery_details.django.html'
    context_object_name = 'delivery'

    def get_context_data(self, **kwargs):
        context = super(Overview, self).get_context_data(**kwargs)
        group = self.request.cradmin_role
        context['group'] = group
        context['deadline_has_expired'] = check_if_last_deadline_has_expired(
            group=group)
        context['deliverycount'] = context['deliveries'].count()
        context['status'] = group.get_status()
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            Overview.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
