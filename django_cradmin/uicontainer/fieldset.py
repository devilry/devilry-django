from .container import AbstractContainerRenderable
from . import form_mixins


class FieldSet(AbstractContainerRenderable, form_mixins.FormRenderableChildMixin):
    template_name = "django_cradmin/uicontainer/fieldset.django.html"

    def __init__(self, title, legend_css_class="legend", **kwargs):
        self.title = title
        self.legend_css_class = legend_css_class
        super(FieldSet, self).__init__(**kwargs)

    def get_default_html_tag(self):
        return "fieldset"

    def get_default_bem_block_or_element(self):
        return "fieldset"
