from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views.about_me import AboutMeView


urlpatterns = patterns('devilry_header',
    url('^about_me$',
        login_required(AboutMeView.as_view()),
        name='devilry_header_aboutme')
)