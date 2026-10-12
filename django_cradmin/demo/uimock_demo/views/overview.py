from django_cradmin.viewhelpers import generic


class Overview(generic.StandaloneBaseTemplateView):
    template_name = "uimock_demo/overview.django.html"
