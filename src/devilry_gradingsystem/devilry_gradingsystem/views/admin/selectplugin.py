from django.views.generic import DetailView

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


    def get_context_data(self, **kwargs):
        context = super(SelectPluginView, self).get_context_data(**kwargs)
        # for plugin in gradingsystempluginregistry:
            # print unicode(plugin.title)
        context['pluginregistry'] = gradingsystempluginregistry.iter_with_assignment(self.object)
        return context