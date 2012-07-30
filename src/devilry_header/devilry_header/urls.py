from django.conf.urls.defaults import patterns, url

from .rest import UserInfo

urlpatterns = patterns('devilry_header',
                       url(r'^userinfo', UserInfo.as_view()),
                      )

