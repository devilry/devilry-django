from django.contrib.auth import get_user_model
from django.http import Http404
from django.views.generic import TemplateView
from django_cradmin import crapp

from devilry.apps.core.models import Assignment


class ContactView(TemplateView):
    template_name = 'devilry_student/cradmin_group/contactapp/contact.django.html'
    context_object_name = 'delivery'

    def dispatch(self, request, *args, **kwargs):
        group = request.cradmin_role
        if group.assignment.anonymizationmode != Assignment.ANONYMIZATIONMODE_OFF:
            raise Http404()
        else:
            return super(ContactView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        group = self.request.cradmin_role
        context['group'] = group
        context['examinerusers'] = list(
            get_user_model().objects
            .filter(id__in=group.examiners.values_list('user_id', flat=True))
            .prefetch_related_primary_email())
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ContactView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
