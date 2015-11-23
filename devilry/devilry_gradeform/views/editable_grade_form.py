
from django_cradmin import renderable


class AbstractEditableRenderer(renderable.AbstractRenderable):
    """
    """


class EditableGradeForm(AbstractEditableRenderer):
    """

    """

class AdvancedEditableGradeForm(EditableGradeForm):

    template_name = 'devilry_gradeform/advanced.gradeform.django.html'

    def __init__(self, assignment, feedbackset):
        self.assignment = assignment
        self.feedbackset = feedbackset

    def get_template_context_object(self, request=None):

        context = super(AdvancedEditableGradeForm, self).get_context_data()

        return context
