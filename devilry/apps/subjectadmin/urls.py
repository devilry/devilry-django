from django.conf.urls.defaults import patterns
from devilry.apps.jsapp.views import create_app_urls

from rest.group import RestGroup

urlpatterns = patterns('devilry.apps.subjectadmin',
                       RestGroup.create_url("restgroup", "restgroup-api", "1.0"),
                       *create_app_urls(appname='subjectadmin',
                                        with_css=True,
                                        include_old_exjsclasses=True,
                                        libs=['jsapp', 'themebase']))
