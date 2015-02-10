from django.http import Http404
from django.views.generic import TemplateView
from django_cradmin import crapp


class ContactView(TemplateView):
    template_name = 'devilry_student/cradmin_group/contactapp/contact.django.html'
    context_object_name = 'delivery'

    def dispatch(self, request, *args, **kwargs):
        group = request.cradmin_role
        if group.assignment.anonymous:
            raise Http404()
        else:
            return super(ContactView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ContactView, self).get_context_data(**kwargs)
        group = self.request.cradmin_role
        context['group'] = group
        context['examiners'] = list(group.examiners.all())
        return context


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ContactView.as_view(),
            name=crapp.INDEXVIEW_NAME),
    ]
