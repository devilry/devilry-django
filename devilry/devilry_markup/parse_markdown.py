import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
# from markdown.extensions.fenced_code import 

from devilry.devilry_markup.markdown_extensions.code_diff import CodeDiffExtension
from devilry.devilry_markup.markdown_extensions.latex_math import LatexMathExtension, LatexMathInlineExtension


def markdown_full(inputMarkdown):
    md = markdown.Markdown(
        output_format='xhtml5',
        safe_mode="escape",
        extensions=[
            CodeDiffExtension(),
            LatexMathExtension(),
            LatexMathInlineExtension(),
            CodeHiliteExtension(
                guess_lang=False,
                linenums=False
            ), # Syntax hilite code
            'fenced_code', # Support github style code blocks
            'nl2br', # Support github style newline handling
            'sane_lists', # Break into new ul/ol tag when the next line starts with another class of list indicator
            'def_list', # Support definition lists
            'tables', # Support tables
        ])
    html = md.convert(inputMarkdown)
    html = html.replace('{{', '{ {').replace('}}', '} }')
    return html
