import debug_toolbar
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import urlpatterns as staticfiles_urlpatterns

from devilry.project.common.default_urls import devilry_urls


urlpatterns = [
    url(r'^__debug__/', include(debug_toolbar.urls)),
    # url(r'^devilry_sandbox/', include('devilry.devilry_sandbox.urls')),
]

urlpatterns.extend(devilry_urls)
urlpatterns.extend(staticfiles_urlpatterns)
