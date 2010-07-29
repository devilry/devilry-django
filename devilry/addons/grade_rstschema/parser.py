#!/usr/bin/env python

from docutils.parsers.rst import Parser
from docutils.utils import new_document, SystemMessage, Reporter, \
    decode_path
from docutils import nodes
from docutils import frontend


class RstValidationError(Exception):
    def __init__(self, level, line, message):
        self.level = level
        self.line = line
        self.message = message

    def __str__(self):
        return 'line %s: %s' % (self.line, self.message)

class ExceptionReporter(Reporter):
    def __init__(self, source):
        Reporter.__init__(self, source,
                report_level = 0,
                halt_level = 0,
                stream = '',  # suppress output to terminal (only use exceptions)
                debug = 0,
                encoding = 'utf-8')

    def system_message(self, level, message, *children, **kwargs):
        raise RstValidationError(level, kwargs.get('line'), message)


def rstdoc_from_string(rst):
    parser = Parser()
    settings = frontend.OptionParser().get_default_values()
    settings.tab_width = 4
    settings.pep_references = False
    settings.rfc_references = False
    settings.embed_stylesheet = False

    source_path = decode_path('string')
    reporter = ExceptionReporter(source_path)
    document = nodes.document(settings, reporter, source=source_path)
    document.note_source(source_path, -1)

    parser.parse(rst, document)
    return document



if __name__ == "__main__":
    import sys
    import text
    import html
    import field

    def show_help():
        print "Usage:"
        print "   %s create <definition-file> <html|text>" % sys.argv[0]
        print "   %s validate <definition-file> <input-file>" % sys.argv[0]
        raise SystemExit()

    field.register_directive() # register .. field:: with rst

    if len(sys.argv) != 4:
        show_help()
    action = sys.argv[1]
    definition_file = sys.argv[2]
    rst = open(definition_file, 'rb').read()

    if action == 'create':
        fmt = sys.argv[3]
        if fmt == 'html':
            p = html.input_form(rst)
            print p
        elif fmt == 'text':
            print text.examiner_format(rst)
        else:
            show_help()

    elif action == 'validate':
        try:
            document = rstdoc_from_string(rst)
        except RstValidationError, e:
            print e
            sys.exit()
        input_file = sys.argv[3]
        input = open(input_file, 'rb').read()
        input = text.strip_messages(input)
        fields = field.extract_fields(document)
        ok, output = text.validate_input(input, fields)
        open(input_file, 'wb').write(output)
        print output
    else:
        show_help()
