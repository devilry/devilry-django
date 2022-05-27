import re
from django.template.loader import render_to_string
from markdown.preprocessors import Preprocessor
from markdown import Extension
from django.utils.safestring import mark_safe
from xml.sax.saxutils import quoteattr


class LatexMathPreprocessor(Preprocessor):
    RE_FENCE = re.compile(
        r'(?P<fence>^\$mathblock\$)'                    # opening fence
        r'(?P<code>.*?)'                                # the code block
        r'(?P<closingfence>^\$/mathblock\$)[ ]*$',      # closing fence
        re.DOTALL | re.MULTILINE
    )

    def get_variant(self):
        return 'block'

    def _render_latex_math(self, latex_code) -> str:
        return render_to_string(
            template_name='devilry_markup/latex_math.html',
            context={
                'variant': self.get_variant(),
                'latex_code_attr_safe': mark_safe(quoteattr(latex_code)),
            }
        ).replace('\n', '')

    def run(self, lines):
        text = '\n'.join(lines)
        text = text.replace('\r\n', '\n')
        while 1:
            match = self.RE_FENCE.search(text)
            if match:
                latex_code = match.group('code').strip()
                latex_html = self._render_latex_math(latex_code=latex_code)
                placeholder = self.md.htmlStash.store(latex_html)
                text = f'{text[:match.start()]}{placeholder}{text[match.end():]}'
            else:
                break
        return text.split('\n')


class LatexMathInlinePreprocessor(LatexMathPreprocessor):
    RE_FENCE = re.compile(
        r'(?P<fence>\$math\$)'                    # opening fence
        r'(?P<code>.*?)'                          # the code block
        r'(?P<closingfence>\$/math\$)',           # closing fence
        re.DOTALL | re.MULTILINE
    )

    def get_variant(self):
        return 'inline'


class LatexMathExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.register(LatexMathPreprocessor(md), 'latexmath', 20)


class LatexMathInlineExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.register(LatexMathInlinePreprocessor(md), 'latexmathinline', 21)
