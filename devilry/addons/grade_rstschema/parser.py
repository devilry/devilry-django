#!/usr/bin/env python

from docutils.parsers.rst import Parser, directives
from docutils.utils import new_document
from docutils import nodes
from docutils.parsers.rst import Directive

from spec import Spec



def rstdoc_from_string(rst):
    parser = Parser()
    document = new_document("test")
    document.settings.tab_width = 4
    document.settings.pep_references = 1
    document.settings.rfc_references = 1
    parser.parse(rst, document)
    return document



class appraisal(nodes.Element): pass

class Appraisal(Directive):

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
            'default': directives.unchanged_required}
    has_content = False

    def run(self):
        spec = directives.unchanged_required(self.arguments[0])
        self.options['spec'] = spec
        node = appraisal(rawsource='', **self.options)
        node.spec = Spec.parse(spec)
        return [node]


class AppraisalExtractor(object):
    def __init__(self, document):
        self.document = document
        self.appraisals = []

    def dispatch_visit(self, node):
        if node.tagname == 'appraisal':
            self.appraisals.append(node)

def extract_appraisals(document):
    ac = AppraisalExtractor(document)
    document.walk(ac)
    return ac.appraisals




if __name__ == "__main__":
    import sys
    from docutils.parsers.rst import directives
    from docutils.core import publish_from_doctree
    import text

    def show_help():
        print "Usage:"
        print "   %s create <definition-file> <html|text>" % sys.argv[0]
        print "   %s validate <definition-file> <input-file>" % sys.argv[0]
        raise SystemExit()

    directives.register_directive('appraisal', Appraisal)

    if len(sys.argv) != 4:
        show_help()
    action = sys.argv[1]
    definition_file = sys.argv[2]
    rst = open(definition_file, 'rb').read()
    document = rstdoc_from_string(rst)

    if action == 'create':
        fmt = sys.argv[3]
        if fmt == 'html':
            p = publish_from_doctree(document, writer=SchemaHTMLWriter())
            print p
        elif fmt == 'text':
            print text.examiner_format(rst)
        else:
            show_help()
    elif action == 'validate':
        input_file = sys.argv[3]
        input = open(input_file, 'rb').read()
        input = text.strip_messages(input)
        appraisals = extract_appraisals(document)
        ok, output = text.validate_input(input, appraisals)
        open(input_file, 'wb').write(output)
        print output
    else:
        show_help()
