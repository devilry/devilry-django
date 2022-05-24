from django.views.generic import TemplateView


class WcagDebugView(TemplateView):
    template_name = 'devilry_theme3/wcag-debug.django.html'
