from docutils.parsers.rst import directives
from docutils.nodes import Element
from docutils.parsers.rst import Directive

from spec import Spec


class field(Element): pass

class Field(Directive):

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
            'default': directives.unchanged_required}
    has_content = False

    def run(self):
        spec = directives.unchanged_required(self.arguments[0])
        self.options['spec'] = spec
        node = field(rawsource='', **self.options)
        node.spec = Spec.parse(spec)
        node.default = self.options.get('default')
        return [node]


class FieldExtractor(object):
    def __init__(self, document):
        self.document = document
        self.fields = []

    def dispatch_visit(self, node):
        if node.tagname == 'field':
            self.fields.append(node)

def extract_fields(document):
    ac = FieldExtractor(document)
    document.walk(ac)
    return ac.fields


def register_directive():
    directives.register_directive('field', Field)
