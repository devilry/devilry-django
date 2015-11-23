from django.conf.urls import patterns
from django.conf.urls import url
from devilry.apps.core.models import Assignment
from devilry.devilry_gradeform.views.grade_form import AbstractGradeForm
from devilry.devilry_group.models import FeedbackSet

from views import grade_form

urlpatterns = patterns(
    'devilry.devilry_gradeform',
    url(r'^advanced_editable',
        grade_form.AbstractGradeForm.render_editable(AbstractGradeForm(), Assignment(), FeedbackSet()),
        name='devilry-gradeform-advanced-editable'),
)