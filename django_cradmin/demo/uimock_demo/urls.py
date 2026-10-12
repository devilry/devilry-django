from django.urls import path, re_path

from django_cradmin import viewhelpers

from .views import overview

urlpatterns = [
    re_path(
        r"^simple/(?P<mockname>.+)?$",
        viewhelpers.uimock.UiMock.as_view(template_directory="uimock_demo/simple/"),
        name="cradmin_uimock_demo_simple",
    ),
    path("", overview.Overview.as_view(), name="cradmin_uimock_demo"),
]
