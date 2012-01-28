from django.conf.urls.defaults import patterns
from devilry.apps.jsapp.views import create_urls

urlpatterns = patterns('devilry.apps.subjectadmin',
                       *create_urls('subjectadmin',
                                    with_css=True,
                                    include_old_exjsclasses=True,
                                    libs=['jsapp', 'themebase']))
