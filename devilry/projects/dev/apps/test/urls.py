from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required

from views import TestView

urlpatterns = patterns('devilry.projects.dev.apps.test',
                       url(r'^$',
                           login_required(TestView.as_view())))
