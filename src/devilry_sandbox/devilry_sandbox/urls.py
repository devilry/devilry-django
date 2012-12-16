from django.conf.urls.defaults import patterns, url

from .views import CreatePeriodView



urlpatterns = patterns('devilry_sandbox',
    url('^createperiod$', CreatePeriodView.as_view()),
)
