class FieldWrapperRenderableChildMixin(object):
    """
    Mixin class for renderables that are children of :class:`.FieldWrapper`.
    """

    @property
    def field_wrapper_renderable(self):
        return self.properties["field_wrapper_renderable"]


class FieldChildMixin(FieldWrapperRenderableChildMixin):
    """
    Mixin class for renderables that are children of :class:`.FieldWrapper`.
    """

    @property
    def field_renderable(self):
        return self.properties["field_renderable"]


class FormRenderableChildMixin(object):
    @property
    def formrenderable(self):
        return self.properties["formrenderable"]
