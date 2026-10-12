from django.conf import settings
from django.contrib.auth import views as auth_views


class CradminLogoutView(auth_views.LogoutView):
    http_method_names = ["post", "options", "get"]
    template_name = "cradmin_authenticate/logout.django.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["LOGIN_URL"] = str(settings.LOGIN_URL)
        return context


def cradmin_logoutview(request, template_name="cradmin_authenticate/logout.django.html"):
    return CradminLogoutView.as_view(template_name=template_name)(request)
