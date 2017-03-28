from __future__ import unicode_literals

from django.forms import forms
from django_cradmin.viewhelpers.crudbase import OnlySaveButtonMixin
from django_cradmin.viewhelpers.update import UpdateView
from django.views.generic import RedirectView, FormView
from django.utils import timezone

from devilry.apps.core import models as coremodels


class PublishNowRedirectView(RedirectView):
    http_method_names = ['post']
    permanent = False

    def __publish_assignment_now(self):
        assignment = self.request.cradmin_role
        assignment.publishing_time = timezone.now()
        assignment.save()

    def get_redirect_url(self, *args, **kwargs):
        self.__publish_assignment_now()
        return self.request.cradmin_app.reverse_appindexurl()


class AssignmentPublishingTimeUpdateView(OnlySaveButtonMixin, UpdateView):
    model = coremodels.Assignment

    fields = ['publishing_time']

    def get_queryset_for_role(self, role):
        return self.model.objects.filter(id=self.kwargs['pk'])
