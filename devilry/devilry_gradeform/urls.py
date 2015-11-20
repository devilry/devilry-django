from django.conf.urls import patterns
from django.conf.urls import url

from views import advanced_grade_form

urlpatterns = patterns(
    'devilry.devilry_gradeform',
    url(r'^advanced_editable',
        advanced_grade_form.AdvancedEditableGradeForm.render_editable,
        name='devilry-gradeform-advanced-editable'),
)