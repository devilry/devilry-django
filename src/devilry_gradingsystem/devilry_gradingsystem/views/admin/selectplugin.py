from django.views.generic import DetailView
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from devilry.apps.core.models import Assignment
from devilry_gradingsystem.pluginregistry import gradingsystempluginregistry


class SelectPluginView(DetailView):
    template_name = 'devilry_gradingsystem/admin/selectplugin.django.html'
    model = Assignment
    pk_url_kwarg = 'assignmentid'
    context_object_name = 'assignment'

    def get_queryset(self):
        return Assignment.objects.filter_admin_has_access(self.request.user)\
            .select_related(
                'parentnode', # Period
                'parentnode__parentnode') # Subject

    def _get_next_page_url(self, selected_plugin_id):
        assignment = self.get_object()
        PluginApiClass = gradingsystempluginregistry.get(selected_plugin_id)
        pluginapi = PluginApiClass(assignment)
        if pluginapi.requires_configuration:
            return pluginapi.get_configuration_url()
        elif pluginapi.sets_max_points_automatically:
            # TODO: Update to the specify points view
            return reverse('devilry_gradingsystem_admin_selectplugin', kwargs={
                'assignmentid': assignment.id,
            })
        else:
            # TODO: Update to the "Choose how students are graded" view
            return reverse('devilry_gradingsystem_admin_selectplugin', kwargs={
                'assignmentid': assignment.id,
            })


    def get(self, *args, **kwargs):
        selected_plugin_id = self.request.GET.get('selected_plugin_id')
        if selected_plugin_id:
            return redirect(self._get_next_page_url(selected_plugin_id))
        else:
            return super(SelectPluginView, self).get(*args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(SelectPluginView, self).get_context_data(**kwargs)
        # for plugin in gradingsystempluginregistry:
            # print unicode(plugin.title)
        context['pluginregistry'] = gradingsystempluginregistry.iter_with_assignment(self.object)
        return context