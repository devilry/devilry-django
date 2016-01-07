from django.conf.urls import patterns, include
from django.conf.urls import url

from devilry.devilry_gradeform.views.grade_form import AbstractGradeForm, AdvancedGradeForm
from devilry.devilry_gradeform.views.setup_create_gradeform import CreateGradeForm

from views import grade_form

urlpatterns = patterns(
    'devilry.devilry_gradeform',

    url(r'^create/(?P<assignment_id>[0-9]+)',
        CreateGradeForm.as_view(),
        name='create-setup-gradeform'),

    # url(r'^$',
    #     grade_form.AdvancedGradeForm.render_setup(AdvancedGradeForm(), None),
    #     name='devilry-gradeform-setup'),
    # url(r'^$',
    #     grade_form.AdvancedGradeForm.render_editable(AdvancedGradeForm(), None, None),
    #     name='devilry-gradeform-advanced-editable'),
)