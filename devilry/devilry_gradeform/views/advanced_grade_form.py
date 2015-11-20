from . import grade_form
from django.shortcuts import render


class AdvancedGradeForm(grade_form.AbstractEditableRenderer):

    def get_setuprenderer_class(self):
        return None

    def get_editablerenderer_class(self):
        return AdvancedEditableGradeForm

    def get_viewablerenderer_class(self):
        return None


class AdvancedEditableGradeForm(AdvancedGradeForm):

    template_name = 'devilry_gradeform/advanced.gradeform.django.html'

    def __init__(self, assignment, feedbackset):
        self.assignment = assignment
        self.feedbackset = feedbackset

    def get_template_context_object(self, request=None):

        context = super(AdvancedEditableGradeForm, self).get_context_data()

        return context
