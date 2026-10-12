from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views import static

from django_cradmin.demo.no_role_demo.cradmin import NoRoleCrAdminInstance
from django_cradmin.demo.project.demo.views.demo_overview import DemoView
from django_cradmin.demo.uicontainerdemo.uicontainerdemo_cradmin_instance import UIContainerDemoCrAdminInstance

admin.site.login = login_required(admin.site.login)

urlpatterns = [
    path("authenticate/", include("django_cradmin.apps.cradmin_authenticate.urls")),
    path("resetpassword/", include("django_cradmin.apps.cradmin_resetpassword.urls")),
    path("activate_account/", include("django_cradmin.apps.cradmin_activate_account.urls")),
    path("register/", include("django_cradmin.apps.cradmin_register_account.urls")),
    path("cradmin_email/", include("django_cradmin.apps.cradmin_email.urls")),
    path("djangoadmin/", admin.site.urls),
    path("javascript_demos/", include("django_cradmin.demo.cradmin_javascript_demos.urls")),
    path("no_role_demo/", include(NoRoleCrAdminInstance.urls())),
    path("uicontainerdemo/", include(UIContainerDemoCrAdminInstance.urls())),
    path("uimock_demo/", include("django_cradmin.demo.uimock_demo.urls")),
    path("", DemoView.as_view()),
    path("media/<path:path>", static.serve, {"document_root": settings.MEDIA_ROOT}),
]
