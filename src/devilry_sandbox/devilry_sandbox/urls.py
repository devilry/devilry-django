from django.conf.urls.defaults import patterns, url

from .views import CreateSubjectIntroView
from .views import CreateSubjectCreateView



urlpatterns = patterns('devilry_sandbox',
    url('^createsubject-intro$', CreateSubjectIntroView.as_view()),
    url('^createsubject-create$', CreateSubjectCreateView.as_view(), name='devilry-sandbox-createsubject-create')
)
