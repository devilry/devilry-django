import json

from django_cradmin import renderable


class AdvancedViewableGradeForm(renderable.AbstractRenderable):
    """

    """
    template_name = "devilry_gradeform/advanced.gradeform.django.html"

    def __init__(self, assignment, feedbackset):
        self.assignment = assignment
        self.feedbackset = feedbackset

    def get_template_context_object(self, request=None):
        context = super(AdvancedViewableGradeForm, self).get_context_data()
        context['gradeform_type'] = 'advanced'
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
