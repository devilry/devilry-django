from django.conf.urls import patterns, url

from .views import CreateSubjectIntroView
from .views import CreateSubjectCreateView
from .views import CreateSubjectSuccessView



urlpatterns = patterns('devilry_sandbox',
    url('^createsubject-intro$', CreateSubjectIntroView.as_view()),
    url('^createsubject-create$', CreateSubjectCreateView.as_view(),
        name='devilry-sandbox-createsubject-create'),
    url('^createsubject-success/(?P<unique_number>\d+)$', CreateSubjectSuccessView.as_view(),
        name='devilry-sandbox-createsubject-success'),
)
