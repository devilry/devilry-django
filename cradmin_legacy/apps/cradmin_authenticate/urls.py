from django.urls import path

from cradmin_legacy.apps.cradmin_authenticate.views.login import LoginView
from cradmin_legacy.apps.cradmin_authenticate.views.logout import cradmin_logoutview

urlpatterns = [
    path("login", LoginView.as_view(), name="cradmin-authenticate-login"),
    path("logout", cradmin_logoutview, name="cradmin-authenticate-logout"),
]
