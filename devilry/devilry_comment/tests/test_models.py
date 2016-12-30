import os
import shutil

from django import test
from django.core.files.base import ContentFile
from model_mommy import mommy

from devilry.devilry_comment.models import CommentFile, Comment


class AbstractTestCase(test.TestCase):
    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)


class TestCommentModel(AbstractTestCase):
    def test_delete_comment_model_deletes_files(self):
        testcomment = mommy.make('devilry_comment.Comment')
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        testcomment.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_bulk_delete_comment_model_deletes_files(self):
        testcomment = mommy.make('devilry_comment.Comment')
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        Comment.objects.all().delete()
        self.assertFalse(os.path.exists(filepath))


class TestCommentFileModel(AbstractTestCase):
    def test_empty_file_field_is_bool_false(self):
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     file='')
        self.assertFalse(bool(testcommentfile.file))

    def test_set_file_field_is_bool_true(self):
        testcommentfile = mommy.make('devilry_comment.CommentFile')
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        self.assertTrue(bool(testcommentfile.file))

    def test_delete_removes_file(self):
        testcommentfile = mommy.make('devilry_comment.CommentFile')
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        testcommentfile.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_delete_handles_file_not_set(self):
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     file='')
        testcommentfile.delete()  # No exception

    def test_delete_handles_file_does_not_exist_set(self):
        testcommentfile = mommy.make('devilry_comment.CommentFile',
                                     file='')
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        os.remove(filepath)
        testcommentfile.delete()  # No exception

    def test_bulk_delete_removes_file(self):
        testcommentfile = mommy.make('devilry_comment.CommentFile')
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        CommentFile.objects.all().delete()
        self.assertFalse(os.path.exists(filepath))


class TestCommentFileImageModel(AbstractTestCase):
    def test_empty_image_field_is_bool_false(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage',
                                      image='')
        self.assertFalse(bool(testcommentimage.image))

    def test_set_image_field_is_bool_true(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage')
        testcommentimage.image.save('testimage.txt', ContentFile('test'))
        self.assertTrue(bool(testcommentimage.image))

    def test_empty_thumbnail_field_is_bool_false(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage',
                                      thumbnail='')
        self.assertFalse(bool(testcommentimage.image))

    def test_set_thumbnail_field_is_bool_true(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage')
        testcommentimage.thumbnail.save('testimage.txt', ContentFile('test'))
        self.assertTrue(bool(testcommentimage.thumbnail))

    def test_delete_removes_image(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage')
        testcommentimage.image.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.image.path
        self.assertTrue(os.path.exists(filepath))
        testcommentimage.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_delete_removes_thumbnail(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage')
        testcommentimage.thumbnail.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.thumbnail.path
        self.assertTrue(os.path.exists(filepath))
        testcommentimage.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_delete_handles_image_not_set(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage',
                                      image='')
        testcommentimage.delete()  # No exception

    def test_delete_handles_thumbnail_not_set(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage',
                                      thumbnail='')
        testcommentimage.delete()  # No exception

    def test_delete_handles_image_does_not_exist_set(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage',
                                      image='')
        testcommentimage.image.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.image.path
        os.remove(filepath)
        testcommentimage.delete()  # No exception

    def test_delete_handles_thumbnail_does_not_exist_set(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage',
                                      thumbnail='')
        testcommentimage.thumbnail.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.thumbnail.path
        os.remove(filepath)
        testcommentimage.delete()  # No exception

    def test_bulk_delete_removes_image(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage')
        testcommentimage.image.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.image.path
        self.assertTrue(os.path.exists(filepath))
        CommentFile.objects.all().delete()
        self.assertFalse(os.path.exists(filepath))

    def test_bulk_delete_removes_thumbnail(self):
        testcommentimage = mommy.make('devilry_comment.CommentFileImage')
        testcommentimage.thumbnail.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.thumbnail.path
        self.assertTrue(os.path.exists(filepath))
        CommentFile.objects.all().delete()
        self.assertFalse(os.path.exists(filepath))
