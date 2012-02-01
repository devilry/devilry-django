from django.conf.urls.defaults import patterns
from devilry.apps.jsapp.views import create_app_urls

urlpatterns = patterns('devilry.apps.subjectadmin',
                       *create_app_urls(appname='subjectadmin',
                                        with_css=True,
                                        include_old_exjsclasses=True,
                                        libs=['jsapp', 'themebase']))
