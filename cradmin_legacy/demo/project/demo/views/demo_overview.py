from django.views.generic import TemplateView


class DemoView(TemplateView):
    template_name = "cradmin_demo/demo-overview.django.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["github_base_url"] = "https://github.com/appressoas/cradmin_legacy/tree/master/cradmin_legacy/demo"
        return context
