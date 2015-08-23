from django.views.generic import DetailView
from devilry.devilry_account.models import User
from django.conf import settings

from devilry.devilry_settings.views import urlsetting_or_unsetview


class AboutMeView(DetailView):
    template_name = "devilry_header/about_me.django.html"
    model = User

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(AboutMeView, self).get_context_data(**kwargs)
        context['logout_url'] = settings.DEVILRY_LOGOUT_URL
        context['wrong_info_url'] = urlsetting_or_unsetview('DEVILRY_WRONG_USERINFO_URL')
        return context
