from django.conf import settings
from django.contrib.staticfiles.urls import urlpatterns as staticfiles_urlpatterns
from django.urls import path, include

from devilry.project.common.default_urls import devilry_urls
from devilry.project.common.http_error_handlers import *  # noqa


urlpatterns = [
    # path('devilry_sandbox/', include('devilry.devilry_sandbox.urls')),
    path('devilry_theme/', include('devilry.devilry_theme3.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns

urlpatterns.extend(devilry_urls)
urlpatterns.extend(staticfiles_urlpatterns)
