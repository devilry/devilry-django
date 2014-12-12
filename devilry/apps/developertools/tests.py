import unittest
from .management.commands.dev_build_extjs import SimpleJsFile

class TestJsFile(unittest.TestCase):
    def testMultilineCommentPattern(self):
        self.assertEquals(SimpleJsFile.MULTILINE_COMMENT_PATT.sub('', 'hello /**some \n\n comments \n\t here*/world'),
                          'hello world')

    def testSingleLineCommentPattern(self):
        self.assertEquals(SimpleJsFile.SINGLELINE_COMMENT_PATT.sub('', 'hello // this is a test\nworld'),
                          'hello \nworld')
