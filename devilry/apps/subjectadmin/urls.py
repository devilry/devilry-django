from django.conf.urls.defaults import patterns
from devilry.apps.guibase.views import create_urls

urlpatterns = patterns('devilry.apps.subjectadmin',
                       *create_urls('subjectadmin', with_css=True))
