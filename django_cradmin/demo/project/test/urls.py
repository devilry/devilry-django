from django.urls import include, path


urlpatterns = [
    path("cradmin_authenticate/", include("django_cradmin.apps.cradmin_authenticate.urls")),
    path("cradmin_resetpassword/", include("django_cradmin.apps.cradmin_resetpassword.urls")),
    path("cradmin_activate_account/", include("django_cradmin.apps.cradmin_activate_account.urls")),
    path("cradmin_register_account/", include("django_cradmin.apps.cradmin_register_account.urls")),
]
