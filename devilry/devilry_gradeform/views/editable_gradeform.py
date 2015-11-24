import json
from crispy_forms.layout import Field, Layout

from django import forms

from crispy_forms import helper

from django_cradmin import renderable
from django_cradmin.viewhelpers import create

class AbstractEditableRenderer(renderable.AbstractRenderable, create.CreateView):
    """
    """
    template_name = "devilry_gradeform/advanced.editable.gradeform.django.html"
    model = "AdvancedEditableGradeForm"


class AdvancedEditableGradeForm(AbstractEditableRenderer):
    """
    """

    test = forms.CharField(label="yay")

    def __init__(self, assignment, feedbackset):
        self.assignment = assignment
        self.feedbackset = feedbackset

    def get_template_context_object(self, request=None):
        context = super(AdvancedEditableGradeForm, self).get_context_data()
        # context['gradeform_type'] = 'advanced'
        # print self.feedbackset.gradeform_json
        data = json.loads(self.assignment.gradeform_setup_json)

        return context
