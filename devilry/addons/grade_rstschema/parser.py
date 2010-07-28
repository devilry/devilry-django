#!/usr/bin/env python

from docutils.parsers.rst import Parser
from docutils.utils import new_document


def rstdoc_from_string(rst):
    parser = Parser()
    document = new_document("string")
    document.settings.tab_width = 4
    document.settings.pep_references = False
    document.settings.rfc_references = False
    document.settings.embed_stylesheet = False
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
        document = rstdoc_from_string(rst)
        input_file = sys.argv[3]
        input = open(input_file, 'rb').read()
        input = text.strip_messages(input)
        fields = field.extract_fields(document)
        ok, output = text.validate_input(input, fields)
        open(input_file, 'wb').write(output)
        print output
    else:
        show_help()
