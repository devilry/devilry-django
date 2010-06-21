from docutils.core import publish_from_doctree, publish_parts
from docutils.writers import html4css1


class SchemaHTMLWriter(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = SchemaHTMLTranslator

class SchemaHTMLTranslator(html4css1.HTMLTranslator):
    def __init__(self, *args, **kwargs):
        html4css1.HTMLTranslator.__init__(self, *args, **kwargs)
        self.field_id = 0

    def visit_field(self, node):
        attrs = {'class': 'rstschemafield'}
        self.body.append(self.starttag(node, 'div', **attrs))
        node.spec.create_html_formfield(node, 'field_%s' % self.field_id, self)
        self.field_id += 1

    def depart_field(self, node):
        self.body.append('</div>')
        pass


def input_form(rst):
    parts = publish_parts(rst, writer=SchemaHTMLWriter(), settings_overrides={})
    return parts["fragment"]
