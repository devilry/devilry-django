from django.conf.urls import url

from devilry.devilry_gradeform.views.setup_create_gradeform import CreateGradeForm

urlpatterns = [
    url(r'^create/(?P<assignment_id>[0-9]+)', CreateGradeForm.as_view(), name='create-setup-gradeform'),
    # url(r'^$',
    #     grade_form.AdvancedGradeForm.render_setup(AdvancedGradeForm(), None),
    #     name='devilry-gradeform-setup'),
    # url(r'^$',
    #     grade_form.AdvancedGradeForm.render_editable(AdvancedGradeForm(), None, None),
    #     name='devilry-gradeform-advanced-editable'),
]
