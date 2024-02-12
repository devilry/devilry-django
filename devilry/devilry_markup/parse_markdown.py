import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
# from markdown.extensions.fenced_code import
from html_sanitizer.django import get_sanitizer

from devilry.devilry_markup.markdown_extensions.code_diff import CodeDiffExtension
from devilry.devilry_markup.markdown_extensions.latex_math import LatexMathExtension, LatexMathInlineExtension


def markdown_full(inputMarkdown):
    sanitizer = get_sanitizer(name='devilry')

    md = markdown.Markdown(
        output_format='xhtml5',
        safe_mode="escape",
        extensions=[
            CodeDiffExtension(),
            CodeHiliteExtension(
                guess_lang=False,
                linenums=False
            ),
            LatexMathInlineExtension(),
            LatexMathExtension(),
            'fenced_code',  # Support github style code blocks
            'sane_lists',  # Break into new ul/ol tag when the next line starts with another class of list indicator
            'def_list',  # Support definition lists
            'tables',  # Support tables
            'nl2br',  # Support github style newline handling
        ])


    html = md.convert(inputMarkdown)
    html = sanitizer.sanitize(html)

    html = html.replace('{{', '{ {').replace('}}', '} }')
    return html
