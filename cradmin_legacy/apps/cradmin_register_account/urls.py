from django.urls import path

from cradmin_legacy.apps.cradmin_register_account.views.begin import BeginRegisterAccountView
from cradmin_legacy.apps.cradmin_register_account.views.email_sent import EmailSentView

urlpatterns = [
    path("begin", BeginRegisterAccountView.as_view(), name="cradmin-register-account-begin"),
    path("email-sent", EmailSentView.as_view(), name="cradmin-register-account-email-sent"),
]
