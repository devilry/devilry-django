from django.urls import path, include

from cradmin_legacy.demo.usermanagerdemo.cradmin import UsermanagerCrAdminInstance
from cradmin_legacy.demo.webdemo.cradmin import WebdemoCrAdminInstance

urlpatterns = [
    path("cradmin_authenticate/", include("cradmin_legacy.apps.cradmin_authenticate.urls")),
    path("cradmin_temporaryfileuploadstore/", include("cradmin_legacy.apps.cradmin_temporaryfileuploadstore.urls")),
    path("cradmin_resetpassword/", include("cradmin_legacy.apps.cradmin_resetpassword.urls")),
    path("cradmin_activate_account/", include("cradmin_legacy.apps.cradmin_activate_account.urls")),
    path("cradmin_register_account/", include("cradmin_legacy.apps.cradmin_register_account.urls")),
    # Demo apps
    path("webdemoadmin/", include(WebdemoCrAdminInstance.urls())),
    path("webdemo/", include("cradmin_legacy.demo.webdemo.urls")),
    path("usermanagerdemo/", include(UsermanagerCrAdminInstance.urls())),
]
