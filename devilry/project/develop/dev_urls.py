from django.contrib.staticfiles.urls import urlpatterns as staticfiles_urlpatterns

from devilry.project.common.default_urls import devilry_urls

urlpatterns = [
    # url(r'^devilry_sandbox/', include('devilry.devilry_sandbox.urls')),
]

urlpatterns.extend(devilry_urls)
urlpatterns.extend(staticfiles_urlpatterns)
