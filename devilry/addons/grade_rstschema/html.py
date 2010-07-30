from docutils.core import publish_parts
from docutils.writers import html4css1

class SchemaHTMLTranslator(html4css1.HTMLTranslator):
    def __init__(self, input_values, validate, *args, **kwargs):
        html4css1.HTMLTranslator.__init__(self, *args, **kwargs)
        self.field_id = 0
        self.input_values = input_values
        self.validate = validate
        self.errors = {}
        self.values = []

    def visit_field(self, node):
        cssclasses = ['rstschema_field']
        field_id = 'rstschema_field_%s' % self.field_id

        # Validate field if enabled
        error = None
        value = None
        value = self.input_values.get(field_id, '')
        if self.validate:
            try:
                node.spec.validate(value)
            except ValueError, e:
                self.errors[field_id] = e
                cssclasses.append('rstschema_field-error')
                error = str(e)
        self.values.append(value)

        attrs = {'class': ' '.join(cssclasses)}
        self.body.append(self.starttag(node, 'div', **attrs))
        if error:
            self.body.append(self.starttag(node, 'ul', **{'class':'errorlist'}))
            self.body.append('<li>%s</li>' % error)
            self.body.append('</ul>')
        node.spec.create_html_formfield(node, field_id, self, value)
        self.field_id += 1

    def depart_field(self, node):
        self.body.append('</div>')


class SchemaHTMLWriter(html4css1.Writer):
    def __init__(self, input_values, validate):
        self.input_values = input_values
        self.validate = validate
        html4css1.Writer.__init__(self)

    def translate(self):
        self.visitor = visitor = SchemaHTMLTranslator(
                self.input_values, self.validate,
                self.document)
        self.document.walkabout(visitor)
        for attr in self.visitor_attributes:
            setattr(self, attr, getattr(visitor, attr))
        self.output = self.apply_template()


def input_form(rst, input_values={}, validate=False):
    #input_values = {
            #'rstschema_field_0': '7',
            #'rstschema_field_1': 'yes',
            #}
    writer = SchemaHTMLWriter(input_values, validate)
    parts = publish_parts(rst,
            writer=writer,
            settings_overrides={})
    return writer.visitor.errors, writer.visitor.values, parts["fragment"]
