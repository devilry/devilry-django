
# Django imports
from django.views.generic import ListView

# CrAdmin imports
from django_cradmin import crapp

# Devilry imports
from devilry.devilry_qualifiesforexam import plugintyperegistry


class SelectPluginView(ListView):

    template_name = 'devilry_qualifiesforexam/selectplugin.django.html'

    def get_queryset(self):
        return self.request.cradmin_instance.get_rolequeryset()

    def get_context_data(self, **kwargs):
        context_data = super(SelectPluginView, self).get_context_data(**kwargs)
        context_data['devilry_role'] = self.request.cradmin_instance.is_admin()
        context_data['headline'] = 'How do students qualify for final exams?'

        plugins = []
        for plugin_class in plugintyperegistry.Registry.get_instance():
            plugin = plugin_class()
            plugins.append(plugin)

        context_data['plugins'] = plugins

        return context_data


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            SelectPluginView.as_view(),
            name=crapp.INDEXVIEW_NAME)
    ]
