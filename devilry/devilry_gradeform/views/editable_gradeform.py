import json
from crispy_forms.layout import Field, Layout, Submit

from django import forms

from crispy_forms import layout

from django_cradmin import renderable
from django_cradmin.viewhelpers import crudbase


class AbstractEditableRenderer(renderable.AbstractRenderable, forms.Form):
    """
    """
    template_name = "devilry_gradeform/advanced.editable.gradeform.django.html"


class AdvancedForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(AdvancedForm, self).__init__(*args, **kwargs)
        counter = 0
        while counter < 3:
            self.fields['test{}'.format(counter)] = forms.CharField(label='Test field {}'.format(counter))
            counter += 1





class AdvancedEditableGradeForm(AbstractEditableRenderer):
    """
    """

    def __init__(self, assignment, feedbackset):
        self.assignment = assignment
        self.feedbackset = feedbackset

    def get_template_context_object(self, request=None):
        context = super(AdvancedEditableGradeForm, self).get_context_data()
        context['gradeform_type'] = 'advanced'
        print self.assignment.gradeform_setup_json
        data = json.loads(self.assignment.gradeform_setup_json)
        context['form'] = AdvancedForm()

        return context
