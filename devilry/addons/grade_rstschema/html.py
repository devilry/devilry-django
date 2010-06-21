from docutils.writers import html4css1


class SchemaHTMLWriter(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = SchemaHTMLTranslator

class SchemaHTMLTranslator(html4css1.HTMLTranslator):
    def visit_field(self, node):
        attrs = {'class': 'field'}
        self.body.append(self.starttag(node, 'div', **attrs))

    def depart_field(self, node):
        self.body.append('</div>')
