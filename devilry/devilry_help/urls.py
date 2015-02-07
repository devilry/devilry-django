from django.conf.urls import patterns, url
from devilry.devilry_help.views import HelpView


urlpatterns = patterns(
    '',
    url('^$', HelpView.as_view(), name='devilry-help'),
)
