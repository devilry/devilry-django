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



def format_text(rst):
    r = re.sub(
            r"\n\n\.\. appraisal::\s+(\S+)\s+:default:\s*(\S+).*",
            r" [\1]\n[[[ \2 ]]]",
            rst, re.MULTILINE)
    r = re.sub(
            r"\n\n\.\. appraisal::\s+(\S+)",
            r"\n[[[  ]]]",
            r, re.MULTILINE)
    return r


def extract_text_input(text):
    return re.findall(r"\[\[\[\s*(.*?)\s*\]\]\]", text)


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
    #print document.pformat()

    if action == 'create':
        fmt = sys.argv[3]
        if fmt == 'html':
            p = publish_from_doctree(document, writer=SchemaHTMLWriter())
            print p
        elif fmt == 'text':
            print format_text(rst)
        else:
            show_help()

    elif action == 'validate':
        text_file = sys.argv[3]
        text = open(text_file, 'rb').read()
        ac = AppraisalCollector(document) 
        document.walk(ac)
        result = extract_text_input(text)
        if len(result) != len(ac.lst):
            raise SystemExit('Invalid input length.')
        s = 0
        for i, a in enumerate(ac.lst):
            r = result[i]
            fmt = a.attributes['format']
            fmt_list = fmt.split('/')
            if not r in fmt_list:
                raise SystemExit('Invalid input: "%s". Valid values: %s' % (r,
                    fmt))

    else:
        show_help()
