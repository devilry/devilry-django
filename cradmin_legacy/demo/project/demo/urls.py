from django.conf import settings
from django.urls import path, include
from django.contrib import admin
from django.views import static

from cradmin_legacy.demo.listfilterdemo.cradmin import ListfilterDemoCrAdminInstance
from cradmin_legacy.demo.login_not_required_demo.cradmin import LoginNotRequiredCrAdminInstance
from cradmin_legacy.demo.multiselect2demo.cradmin import MultiselectDemoCrAdminInstance
from cradmin_legacy.demo.no_role_demo.cradmin import NoRoleCrAdminInstance
from cradmin_legacy.demo.project.demo.views.demo_overview import DemoView
from cradmin_legacy.demo.usermanagerdemo.cradmin import UsermanagerCrAdminInstance
from cradmin_legacy.demo.webdemo.cradmin import WebdemoCrAdminInstance
from cradmin_legacy.superuserui import superuserui_registry

urlpatterns = [
    path("authenticate/", include("cradmin_legacy.apps.cradmin_authenticate.urls")),
    path("resetpassword/", include("cradmin_legacy.apps.cradmin_resetpassword.urls")),
    path("activate_account/", include("cradmin_legacy.apps.cradmin_activate_account.urls")),
    path("register/", include("cradmin_legacy.apps.cradmin_register_account.urls")),
    path("djangoadmin/", admin.site.urls),
    path("webdemo/", include(WebdemoCrAdminInstance.urls())),
    path("listfilterdemo/", include(ListfilterDemoCrAdminInstance.urls())),
    path("multiselect2demo/", include(MultiselectDemoCrAdminInstance.urls())),
    path("login_not_required_demo/", include(LoginNotRequiredCrAdminInstance.urls())),
    path("no_role_demo/", include(NoRoleCrAdminInstance.urls())),
    path("webdemo/", include("cradmin_legacy.demo.webdemo.urls")),
    path("usermanagerdemo/", include(UsermanagerCrAdminInstance.urls())),
    path("cradmin_temporaryfileuploadstore/", include("cradmin_legacy.apps.cradmin_temporaryfileuploadstore.urls")),
    path("", DemoView.as_view()),
    path("media/<path:path>", static.serve, {"document_root": settings.MEDIA_ROOT}),
    path("polls/", include("cradmin_legacy.demo.polls_demo.urls")),
    path("superuser/", include(superuserui_registry.default.make_cradmin_instance_class().urls())),
]
