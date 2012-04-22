from django.conf.urls.defaults import patterns, include
from django.contrib.auth.decorators import login_required

from devilry.apps.jsapp.views import create_app_urls
from views import AppView


urlpatterns = patterns('devilry_subjectadmin',
                       ('rest/',include('devilry_subjectadmin.rest.urls')),
                       ('newui', login_required(AppView.as_view())),
                       *create_app_urls(appname='devilry_subjectadmin',
                                        with_css=True,
                                        include_old_exjsclasses=True,
                                        libs=['jsapp', 'themebase']))
