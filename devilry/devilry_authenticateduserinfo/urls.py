from django.conf.urls import patterns, url

from devilry.devilry_authenticateduserinfo.rest import UserInfo

urlpatterns = patterns('devilry.devilry_authenticateduserinfo',
                       url(r'^userinfo$', UserInfo.as_view()),
                      )

