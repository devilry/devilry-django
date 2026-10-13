from django.urls import include, path

from cradmin_legacy.apps.cradmin_authenticate.views.login import LoginView
from cradmin_legacy.apps.cradmin_authenticate.views.logout import cradmin_logoutview
from cradmin_legacy.apps.cradmin_resetpassword.views.begin import BeginPasswordResetView
from cradmin_legacy.apps.cradmin_resetpassword.views.email_sent import EmailSentView
from cradmin_legacy.apps.cradmin_resetpassword.views.reset import ResetPasswordView

urlpatterns = [
    path("cradmin_authenticate/login", LoginView.as_view(), name="cradmin-authenticate-login"),
    path("cradmin_authenticate/logout", cradmin_logoutview, name="cradmin-authenticate-logout"),
    path("cradmin_resetpassword/begin", BeginPasswordResetView.as_view(), name="cradmin-resetpassword-begin"),
    path("cradmin_resetpassword/email-sent", EmailSentView.as_view(), name="cradmin-resetpassword-email-sent"),
    path("cradmin_resetpassword/reset/<str:token>", ResetPasswordView.as_view(), name="cradmin-resetpassword-reset"),
    path("cradmin_temporaryfileuploadstore/", include("cradmin_legacy.apps.cradmin_temporaryfileuploadstore.urls")),
]
