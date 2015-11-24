from django.conf.urls import patterns
from django.conf.urls import url
from devilry.devilry_gradeform.views.grade_form import AbstractGradeForm, AdvancedGradeForm

from views import grade_form

# urlpatterns = patterns(
#     'devilry.devilry_gradeform',
#     url(r'^advanced_editable',
#         grade_form.AdvancedGradeForm.render_editable(AdvancedGradeForm(), None, None),
#         name='devilry-gradeform-advanced-editable'),
# )