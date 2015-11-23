from django.http import HttpResponse
from devilry.devilry_gradeform.views import editable_grade_form


class AbstractGradeForm(object):
    """
    """

    def render_setup(self, assignment):
        cls = self.get_setuprenderer_class()
        return cls.render()

    def render_editable(self, assignment, feedbackset):
        renderer_class = self.get_editablerenderer_class()
        renderer = renderer_class(assignment, feedbackset)

        return renderer.render()

    def render_viewable(self, assignment, feedbackset):
        cls = self.get_viewablerenderer_class()

        return cls.render()

    def get_setuprenderer_class(self):
        raise NotImplementedError('Must be implemented by subclass')

    def get_editablerenderer_class(self):
        raise NotImplementedError('Must be implemented by subclass')

    def get_viewablerenderer_class(self):
        raise NotImplementedError('Must be implemented by subclass')

    def get_setuprenderer_javascript_library_urls(self):
        return ['']

    def get_setuprenderer_angularjs_libraries(self):
        return ['']

    def get_editablerenderer_javascript_library_urls(self):
        return ['']

    def get_editablerenderer_angularjs_libraries(self):
        return ['']

    def get_viewablerenderer_javascript_library_urls(self):
        return ['']

    def get_viewablerenderer_angularjs_libraries(self):
        return ['']


# class ApprovedNotApprovedGradeForm(AbstractGradeForm):
#
#     def get_setuprenderer_class(self):
#         return ApprovedNotApprovedGradeForm


class AdvancedGradeForm(AbstractGradeForm):

    def get_setuprenderer_class(self):
        return None

    def get_editablerenderer_class(self):
        return editable_grade_form.AdvancedEditableGradeForm

    def get_viewablerenderer_class(self):
        return None
