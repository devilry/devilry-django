#!/usr/bin/env python

from docutils.parsers.rst import Parser, directives
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

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
            #'possible-values': directives.unchanged_required,
            'default': directives.unchanged_required}
    has_content = False

    def run(self):
        #if not 'possible-values' in self.options:
        #    raise self.error("':possible-values: <definition>' is required.")

        value = directives.unchanged_required(self.arguments[0])
        self.options['format'] = value
        node = appraisal(rawsource='', **self.options)
        return [node]



def split_format(format_string):
    return format_string.split('/')


def parse_string(rst):
    parser = Parser()
    document = new_document("test")
    document.settings.tab_width = 4
    document.settings.pep_references = 1
    document.settings.rfc_references = 1
    parser.parse(rst, document)
    return document

def format_text(rst):
    r = re.sub(
            r"\n\n\.\. appraisal::\s+(\S+)\s+:default:\s*(\S+).*",
            r" [\1]\n[[[ \2 ]]]",
            rst, re.MULTILINE)
    r = re.sub(
            r"\n\n\.\. appraisal::\s+(\S+)",
            r" [\1]\n[[[  ]]]",
            r, re.MULTILINE)
    return r

#def extract_text_input(text):
    #return re.findall(r"\[\[\[\s*(.*?)\s*\]\]\]", text)



class AppraisalCollector(object):
    def __init__(self, document, input):
        self.document = document
        self.appraisals = []
        #self.errors = []
        #self.appraisal_index = 0
        #self.input = input

    def dispatch_visit(self, node):
        if node.tagname == 'appraisal':
            #i = self.input[self.appraisal_index]
            fmt = node.attributes['format']
            node.fmt_list = split_format(fmt)
            #if not i in node.fmt_list:
                #self.errors.append('Invalid input: "%s". Valid values: %s' % (
                    #i, fmt))
            self.appraisals.append(node)
            #self.appraisal_index += 1

def extract_appraisals(document):
    ac = AppraisalCollector(document)
    document.walk(ac)
    return ac.appraisals

def validate_text_input(text, appraisals):
    for node in ac.appraisals:
        print node
    if len(input) != len(ac.appraisals):
        raise SystemExit('Invalid input length.')



if __name__ == "__main__":
    import sys
    from docutils.parsers.rst import directives
    from docutils.core import publish_from_doctree
    import re

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
    document = parse_string(rst)

    if action == 'create':
        fmt = sys.argv[3]
        if fmt == 'html':
            p = publish_from_doctree(document, writer=SchemaHTMLWriter())
            print p
        elif fmt == 'text':
            print format_text(rst)
            #print document.pformat()
        else:
            show_help()
    elif action == 'validate':
        text_file = sys.argv[3]
        text = open(text_file, 'rb').read()
        appraisals = extract_appraisals(document)
        validate_text_input(text, appraisals)
    else:
        show_help()
