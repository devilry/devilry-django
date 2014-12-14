from django.conf.urls import patterns, url

from devilry.devilry_sandbox.views import CreateSubjectIntroView
from devilry.devilry_sandbox.views import CreateSubjectCreateView
from devilry.devilry_sandbox.views import CreateSubjectSuccessView



urlpatterns = patterns('devilry.devilry_sandbox',
    url('^createsubject-intro$', CreateSubjectIntroView.as_view()),
    url('^createsubject-create$', CreateSubjectCreateView.as_view(),
        name='devilry-sandbox-createsubject-create'),
    url('^createsubject-success/(?P<unique_number>\d+)$', CreateSubjectSuccessView.as_view(),
        name='devilry-sandbox-createsubject-success'),
)
