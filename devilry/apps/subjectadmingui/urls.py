from django.conf.urls.defaults import patterns
from devilry.apps.guibase.views import create_urls

urlpatterns = patterns('devilry.apps.subjectadmingui',
                       *create_urls('subjectadmingui'))
