from django.views.generic import TemplateView



class DashboardView(TemplateView):
    template_name = "devilry_examiner/dashboard.django.html"
