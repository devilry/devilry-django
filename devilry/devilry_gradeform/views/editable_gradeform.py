import json

from django import forms

from crispy_forms import helper

from django_cradmin import renderable


class AbstractEditableRenderer(renderable.AbstractRenderable):
    """
    """


# class EditableGradeForm(AbstractEditableRenderer):
#     """
#
#     """

class AdvancedEditableGradeForm(AbstractEditableRenderer):

    template_name = "devilry_gradeform/advanced.gradeform.django.html"

    def __init__(self, assignment, feedbackset):
        self.assignment = assignment
        self.feedbackset = feedbackset

    def get_template_context_object(self, request=None):
        context = super(AdvancedEditableGradeForm, self).get_context_data()
        context['gradeform_type'] = 'advanced'
        # print self.feedbackset.gradeform_json
        data = json.loads(self.feedbackset.gradeform_json)
        context['fields'] = []
        for item in data['scheme']:
            context['fields'].append({
                'points_max': item['points_max'],
                'points_achieved': item['points_achieved'],
                'text': item['text'],
                'comment': item['comment']
            })

        return context
