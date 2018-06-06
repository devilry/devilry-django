from django.conf import settings
from django.contrib.staticfiles.urls import urlpatterns as staticfiles_urlpatterns
from django.conf.urls import url, include

from devilry.project.common.default_urls import devilry_urls

urlpatterns = [
    # url(r'^devilry_sandbox/', include('devilry.devilry_sandbox.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns

urlpatterns.extend(devilry_urls)
urlpatterns.extend(staticfiles_urlpatterns)
