from django.views.generic import TemplateView


class SelectPluginView(TemplateView):
    template_name = 'devilry_gradingsystem/admin/selectplugin.django.html'