from django.urls import path

from cradmin_legacy.apps.cradmin_activate_account.views.activate import ActivateAccountView

urlpatterns = [
    path("activate/<str:token>", ActivateAccountView.as_view(), name="cradmin-activate-account-activate"),
]
