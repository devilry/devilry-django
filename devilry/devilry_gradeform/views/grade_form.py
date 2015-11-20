from django_cradmin import renderable

class AbstractGradeForm(object):
    """
    """

    def render_setup(self, assignment):
        cls = self.get_setuprenderer_class()
        return cls.render()

    def render_editable(self, assignment, feedbackset):
        cls = self.get_editablerenderer_class()

        return cls.render()

    def render_viewable(self, assignment, feedbackSet):
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


class AbstractEditableRenderer(AbstractGradeForm, renderable.AbstractRenderable):
    """
    """
