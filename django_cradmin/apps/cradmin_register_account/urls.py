from django.urls import path
from django_cradmin.apps.cradmin_register_account.views import register_account

urlpatterns = [
    path("", register_account.RegisterAccountView.as_view(), name="cradmin-register-account"),
]
