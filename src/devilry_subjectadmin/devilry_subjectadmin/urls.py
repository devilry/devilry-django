from django.conf.urls.defaults import patterns, include
from devilry.apps.jsapp.views import create_app_urls

urlpatterns = patterns('devilry_subjectadmin',
                       ('rest/',include('devilry_subjectadmin.rest.urls')),
                       *create_app_urls(appname='subjectadmin',
                                        with_css=True,
                                        include_old_exjsclasses=True,
                                        libs=['jsapp', 'themebase']))
