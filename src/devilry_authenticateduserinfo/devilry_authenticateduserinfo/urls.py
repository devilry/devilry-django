from django.conf.urls.defaults import patterns, url

from .rest import UserInfo

urlpatterns = patterns('devilry_authenticateduserinfo',
                       url(r'^userinfo$', UserInfo.as_view()),
                      )

