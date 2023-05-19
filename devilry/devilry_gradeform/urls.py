from django.urls import re_path

from devilry.devilry_gradeform.views.setup_create_gradeform import CreateGradeForm

urlpatterns = [
    re_path(r'^create/(?P<assignment_id>[0-9]+)', CreateGradeForm.as_view(), name='create-setup-gradeform'),
]