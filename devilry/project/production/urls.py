from django.contrib.staticfiles.urls import urlpatterns as staticfiles_urlpatterns

from devilry.project.common.default_urls import devilry_urls
from devilry.project.common.http_error_handlers import *  # noqa


urlpatterns = []
urlpatterns.extend(devilry_urls)
urlpatterns.extend(staticfiles_urlpatterns)
