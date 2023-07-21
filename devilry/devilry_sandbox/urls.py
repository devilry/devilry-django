from django.urls import re_path

from devilry.devilry_sandbox.views import CreateSubjectCreateView
from devilry.devilry_sandbox.views import CreateSubjectIntroView
from devilry.devilry_sandbox.views import CreateSubjectSuccessView


urlpatterns = [
    re_path('^createsubject-intro$', CreateSubjectIntroView.as_view()),
    re_path('^createsubject-create$', CreateSubjectCreateView.as_view(),
        name='devilry-sandbox-createsubject-create'),
    re_path('^createsubject-success/(?P<unique_number>\d+)$', CreateSubjectSuccessView.as_view(),
        name='devilry-sandbox-createsubject-success'),
]
