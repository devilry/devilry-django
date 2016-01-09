from django import test
from django.core.files.base import ContentFile
from model_mommy import mommy


# class TestCommentModel(test.TestCase):
#     def test_delete_comment_model_deletes_files(self):
#         testcomment = mommy.make('devilry_comment.Comment')


class TestCommentFileModel(test.TestCase):
    def test_delete_removes_files(self):
        testcomment = mommy.make('devilry_comment.CommentFile',
                                 file=None)
        testcomment.file.save('testfile.txt', ContentFile('test'))
        testcomment.delete()
