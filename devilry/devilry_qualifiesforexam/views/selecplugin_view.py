
# Django imports
from django.views.generic import ListView

# CrAdmin imports
from django_cradmin import crapp
from django_cradmin.viewhelpers import create


class SelectPluginView(create.CreateView):

    template_name = 'devilry_qualifiesforexam/selectplugin.django.html'

    def get_queryset(self):
        return self.request.cradmin_instance.get_rolequeryset()

    def get_context_data(self, **kwargs):
        context_data = super(SelectPluginView, self).get_context_data(**kwargs)
        context_data['devilry_role'] = self.request.cradmin_instance.is_admin()
        context_data['plugin1'] = 'This is plugin 1'
        context_data['plugin2'] = 'This is plugin 2'
        context_data['plugin3'] = 'This is plugin 3'
        context_data['plugin4'] = 'This is plugin 4'

        return context_data


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            SelectPluginView.as_view(),
            name=crapp.INDEXVIEW_NAME)
    ]
