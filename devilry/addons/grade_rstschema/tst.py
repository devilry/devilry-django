from docutils.readers.standalone import Reader
from docutils.parsers.rst import Parser, directives
from docutils.parsers.rst.directives.admonitions import BaseAdmonition
from docutils.utils import new_document
from docutils import nodes
from docutils.parsers.rst import Directive
from docutils.writers import html4css1


class SchemaHTMLWriter(html4css1.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = SchemaHTMLTranslator

class SchemaHTMLTranslator(html4css1.HTMLTranslator):
    def visit_appraisal(self, node):
        attrs = {'class': 'appraisal'}
        self.body.append(self.starttag(node, 'div', **attrs))

    def depart_appraisal(self, node):
        self.body.append('</div>')





class appraisal(nodes.Element): pass

class Appraisal(Directive):

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
            'possible-values': directives.unchanged_required,
            'default': directives.unchanged_required}
    has_content = False


    def run(self):
        if not 'possible-values' in self.options:
            raise self.error("':possible-values: <definition>' is required.")

        if self.arguments:
            value = directives.unchanged_required(self.arguments[0])
            self.options['value'] = value
        node = appraisal(rawsource='', **self.options)
        return [node]
directives.register_directive('appraisal', Appraisal)


class AppraisalCollector(object):
    def __init__(self, document):
        self.document = document
        self.lst = []

    def dispatch_visit(self, node):
        if node.tagname == 'appraisal':
            self.lst.append(node)


def parse_string(rst):
    parser = Parser()
    document = new_document("test")
    document.settings.tab_width = 4
    document.settings.pep_references = 1
    document.settings.rfc_references = 1
    parser.parse(rst, document)
    return document

rst = open('schema.rst', 'rb').read()
document = parse_string(rst)
print document.pformat()

from docutils.core import publish_from_doctree
p = publish_from_doctree(document, writer=SchemaHTMLWriter())
#print p
#print dir(document)

ac = AppraisalCollector(document) 
document.walk(ac)
print ac.lst
