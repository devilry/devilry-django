from django.conf import settings
from django.views.generic import TemplateView


class HelpView(TemplateView):
    template_name = 'devilry_help/help.django.html'

    def get_context_data(self, **kwargs):
        context = super(HelpView, self).get_context_data(**kwargs)
        context['official_help_url'] = settings.DEVILRY_OFFICIAL_HELP_URL
        context['organization_specific_documentation_url'] = getattr(
            settings, 'DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_URL', None)
        context['organization_specific_documentation_text'] = getattr(
            settings, 'DEVILRY_ORGANIZATION_SPECIFIC_DOCUMENTATION_TEXT', None)
        return context
