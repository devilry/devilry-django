from django.conf.urls import patterns
from django.conf.urls import url
from devilry.apps.core.models import Assignment
from devilry.devilry_gradeform.views.grade_form import AbstractGradeForm, AdvancedGradeForm
from devilry.devilry_group.models import FeedbackSet

from views import grade_form

urlpatterns = patterns(
    'devilry.devilry_gradeform',
    url(r'^advanced_editable',
        grade_form.AdvancedGradeForm.render_editable(AdvancedGradeForm(), None, None),
        name='devilry-gradeform-advanced-editable'),
)