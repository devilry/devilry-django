from django.views.generic import DetailView
from django.contrib.auth.models import User
from django.conf import settings


class AboutMeView(DetailView):
    template_name = "devilry_search/about_me.django.html"
    model = User

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(AboutMeView, self).get_context_data(**kwargs)
        context['logout_url'] = settings.DEVILRY_LOGOUT_URL
        return context
