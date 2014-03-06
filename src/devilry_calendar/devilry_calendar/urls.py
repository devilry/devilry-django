from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from .views.calendarviews import CalendarView


urlpatterns = patterns('devilry_calendar',
   url('^$', login_required(CalendarView.as_view()), name='devilry_calendar'),
   )
