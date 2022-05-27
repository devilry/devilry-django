import difflib
import re
import typing
import uuid
from django.template.loader import render_to_string
from markdown.preprocessors import Preprocessor
from markdown import Extension


class CodeDiffPreprocessor(Preprocessor):
    RE_FENCE = re.compile(
        r'(?P<fence>^##<##)'                    # opening fence
        r'[ ]*(?P<diffstyle>\w+)?'              # optional diffstyle
        r'\n'                                   # newline (end of opening fence) 
        r'(?P<code>.*?)(?<=\n)'                 # the code block
        r'(?P=fence)[ ]*$',                     # closing fence
        re.DOTALL | re.MULTILINE
    )
    RE_FENCE_SPLIT = re.compile(r'\n *##>## *\n')

    def _simple_diff(self, a: typing.List[str], b: typing.List[str]) -> str:
        result = []
        diffsequence = difflib.ndiff(a, b)
        for diffline in diffsequence:
            variant = 'common'
            if diffline.startswith('+ '):
                variant = 'add'
            elif diffline.startswith('- '):
                variant = 'remove'
            elif diffline.startswith('? '):
                variant = 'meta'
            diffline = diffline.replace('\n', '<br>')
            result.append(f'<div class="diff__line diff__line--{variant}">{diffline}</div>')
        return ''.join(result)

    def _sidebyside_diff(self, a: typing.List[str], b: typing.List[str]) -> typing.Dict[str, str]:
        result_a = []
        result_b = []
        differ = difflib.Differ()
        diffsequence = differ.compare(a, b)
        for diffline in diffsequence:
            variant = 'common'
            if diffline.startswith('+ '):
                variant = 'add'
            elif diffline.startswith('- '):
                variant = 'remove'
            elif diffline.startswith('? '):
                continue
            diffline = diffline.replace('\n', '<br>')

            line = f'<div class="diff__line diff__line--{variant}">{diffline[2:]}</div>'
            if variant == 'common':
                result_a.append(line)
                result_b.append(line)
            elif variant == 'remove':
                result_a.append(line)
                result_b.append('\n')
            elif variant == 'add':
                result_a.append('\n')
                result_b.append(line)
        return {
            'a': ''.join(result_a),
            'b': ''.join(result_b),
        }

    def _compact_diff(self, a: typing.List[str], b: typing.List[str]) -> str:
        result = []
        diffsequence = difflib.unified_diff(a, b, fromfile='before', tofile='after')
        for diffline in diffsequence:
            variant = 'common'
            if diffline.startswith('+'):
                variant = 'add'
            elif diffline.startswith('-'):
                variant = 'remove'
            elif diffline.startswith('@@'):
                variant = 'meta'
            diffline = diffline.replace('\n', '<br>')
            result.append(f'<div class="diff__line diff__line--{variant}">{diffline}</div>')
        return ''.join(result)

    def _render_diff(self, a: str, b: str, diffstyle: str) -> str:
        a_list = a.splitlines(keepends=True)
        b_list = b.splitlines(keepends=True)
        return render_to_string(
            template_name='devilry_markup/code_diff.html',
            context={
                'diffstyle': diffstyle,
                'simple': self._simple_diff(a_list, b_list),
                'sidebyside': self._sidebyside_diff(a_list, b_list),
                'compact': self._compact_diff(a_list, b_list),
                'dom_id': str(uuid.uuid4())
            }
        ).replace('\n', '')

    def run(self, lines):
        text = '\n'.join(lines)
        text = text.replace('\r\n', '\n')
        while 1:
            match = self.RE_FENCE.search(text)
            if match:
                code = match.group('code')
                diffstyle = match.group('diffstyle') or 'simple'
                from_code, to_code = self.RE_FENCE_SPLIT.split(code, maxsplit=1)
                html_diff = self._render_diff(from_code, to_code, diffstyle=diffstyle)
                placeholder = self.md.htmlStash.store(html_diff)
                text = f'{text[:match.start()]}\n{placeholder}\n{text[match.end():]}'
            else:
                break
        return text.split('\n')


class CodeDiffExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        # md.registerExtension(self)
        md.preprocessors.register(CodeDiffPreprocessor(md), 'codediff', 25)
