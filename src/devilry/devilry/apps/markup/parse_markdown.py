import markdown


def markdown_full(inputMarkdown):
    md = markdown.Markdown(
        output_format='xhtml5',
        safe_mode="escape",
        extensions=[
            'codehilite', # Syntax hilite code
            'fenced_code', # Support github style code blocks
            'nl2br', # Support github style newline handling
            'sane_lists', # Break into new ul/ol tag when the next line starts with another class of list indicator
            'smart_strong', # Do not let hello_world create an <em>,
            'def_list', # Support definition lists
            'tables', # Support tables
        ])
    return md.convert(inputMarkdown)
