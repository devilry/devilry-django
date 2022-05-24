import os
import shutil

from django import test
from django.core.files.base import ContentFile
from model_bakery import baker

from devilry.devilry_comment.models import CommentFile, Comment, CommentFileImage


class AbstractTestCase(test.TestCase):
    def tearDown(self):
        # Ignores errors if the path is not created.
        shutil.rmtree('devilry_testfiles/filestore/', ignore_errors=True)


class TestCommentModel(AbstractTestCase):
    def test_delete_comment_model_deletes_files(self):
        testcomment = baker.make('devilry_comment.Comment')
        testcommentfile = baker.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        testcomment.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_bulk_delete_comment_model_deletes_files(self):
        testcomment = baker.make('devilry_comment.Comment')
        testcommentfile = baker.make('devilry_comment.CommentFile',
                                     comment=testcomment)
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        Comment.objects.all().delete()
        self.assertFalse(os.path.exists(filepath))


class TestCommentFileModel(AbstractTestCase):
    def test_empty_file_field_is_bool_false(self):
        testcommentfile = baker.make('devilry_comment.CommentFile',
                                     file='')
        self.assertFalse(bool(testcommentfile.file))

    def test_set_file_field_is_bool_true(self):
        testcommentfile = baker.make('devilry_comment.CommentFile')
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        self.assertTrue(bool(testcommentfile.file))

    def test_delete_removes_file(self):
        testcommentfile = baker.make('devilry_comment.CommentFile')
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        self.assertTrue(os.path.exists(filepath))
        testcommentfile.delete()
        self.assertFalse(os.path.exists(filepath))
    
    def test_delete_multiple_commentfiles_with_same_file_path_does_not_remove_file(self):
        testcommentfile1 = baker.make('devilry_comment.CommentFile')
        testcommentfile2 = baker.make('devilry_comment.CommentFile')
        testcommentfile1.file.save('testfile.txt', ContentFile('test'))
        testcommentfile2.file = testcommentfile1.file
        testcommentfile2.full_clean()
        testcommentfile2.save()
        filepath = testcommentfile1.file.path
        self.assertEqual(testcommentfile1.file.path, testcommentfile2.file.path)
        self.assertTrue(os.path.exists(filepath))
        testcommentfile1.delete()
        self.assertTrue(os.path.exists(filepath))
    
    def test_delete_multiple_commentfiles_with_same_file_path_sequential_delete_sanity(self):
        testcommentfile1 = baker.make('devilry_comment.CommentFile')
        testcommentfile2 = baker.make('devilry_comment.CommentFile')
        testcommentfile3 = baker.make('devilry_comment.CommentFile')
        testcommentfile1.file.save('testfile.txt', ContentFile('test'))
        testcommentfile2.file = testcommentfile1.file
        testcommentfile2.full_clean()
        testcommentfile2.save()
        testcommentfile3.file = testcommentfile1.file
        testcommentfile3.full_clean()
        testcommentfile3.save()
        filepath = testcommentfile1.file.path
        self.assertTrue(os.path.exists(filepath))
        testcommentfile1.delete()
        self.assertTrue(os.path.exists(filepath))
        testcommentfile2.delete()
        self.assertTrue(os.path.exists(filepath))
        testcommentfile3.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_delete_handles_file_not_set(self):
        testcommentfile = baker.make('devilry_comment.CommentFile',
                                     file='')
        testcommentfile.delete()  # No exception

    def test_delete_handles_file_does_not_exist_set(self):
        testcommentfile = baker.make('devilry_comment.CommentFile',
                                     file='')
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        filepath = testcommentfile.file.path
        os.remove(filepath)
        testcommentfile.delete()  # No exception

    def test_bulk_delete_removes_file(self):
        testcommentfile = baker.make('devilry_comment.CommentFile')
        testcommentfile.file.save('testfile.txt', ContentFile('test'))
        with self.assertRaisesMessage(
            NotImplementedError,
            'Bulk deletion not supported. Delete each CommentFile instead. '
            'This is because multiple CommentFiles can point to the same FileField.path, '
            'and this check is handled in a pre_delete signal.'):
            CommentFile.objects.all().delete()


class TestCommentFileImageModel(AbstractTestCase):
    def test_empty_image_field_is_bool_false(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage',
                                      image='')
        self.assertFalse(bool(testcommentimage.image))

    def test_set_image_field_is_bool_true(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage')
        testcommentimage.image.save('testimage.txt', ContentFile('test'))
        self.assertTrue(bool(testcommentimage.image))

    def test_empty_thumbnail_field_is_bool_false(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage',
                                      thumbnail='')
        self.assertFalse(bool(testcommentimage.image))

    def test_set_thumbnail_field_is_bool_true(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage')
        testcommentimage.thumbnail.save('testimage.txt', ContentFile('test'))
        self.assertTrue(bool(testcommentimage.thumbnail))

    def test_delete_removes_image(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage')
        testcommentimage.image.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.image.path
        self.assertTrue(os.path.exists(filepath))
        testcommentimage.delete()
        self.assertFalse(os.path.exists(filepath))
    
    def test_delete_multiple_commentimages_with_same_image_path_does_not_remove_file(self):
        testcommentimage1 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage2 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage1.image.save('testfile.txt', ContentFile('test'))
        testcommentimage2.image = testcommentimage1.image
        testcommentimage2.full_clean()
        testcommentimage2.save()
        filepath = testcommentimage1.image.path
        self.assertEqual(testcommentimage1.image.path, testcommentimage2.image.path)
        self.assertTrue(os.path.exists(filepath))
        testcommentimage1.delete()
        self.assertTrue(os.path.exists(filepath))
    
    def test_delete_multiple_commentimages_with_same_image_path_sequential_delete_sanity(self):
        testcommentimage1 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage2 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage3 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage1.image.save('testfile.txt', ContentFile('test'))
        testcommentimage2.image = testcommentimage1.image
        testcommentimage2.full_clean()
        testcommentimage2.save()
        testcommentimage3.image = testcommentimage1.image
        testcommentimage3.full_clean()
        testcommentimage3.save()
        filepath = testcommentimage1.image.path
        self.assertTrue(os.path.exists(filepath))
        testcommentimage1.delete()
        self.assertTrue(os.path.exists(filepath))
        testcommentimage2.delete()
        self.assertTrue(os.path.exists(filepath))
        testcommentimage3.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_delete_removes_thumbnail(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage')
        testcommentimage.thumbnail.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.thumbnail.path
        self.assertTrue(os.path.exists(filepath))
        testcommentimage.delete()
        self.assertFalse(os.path.exists(filepath))
    
    def test_delete_multiple_commentimages_with_same_thumbnail_path_does_not_remove_file(self):
        testcommentimage1 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage2 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage1.thumbnail.save('testfile.txt', ContentFile('test'))
        testcommentimage2.thumbnail = testcommentimage1.thumbnail
        testcommentimage2.full_clean()
        testcommentimage2.save()
        filepath = testcommentimage1.thumbnail.path
        self.assertEqual(testcommentimage1.thumbnail.path, testcommentimage2.thumbnail.path)
        self.assertTrue(os.path.exists(filepath))
        testcommentimage1.delete()
        self.assertTrue(os.path.exists(filepath))
    
    def test_delete_multiple_commentimages_with_same_thumbnail_path_sequential_delete_sanity(self):
        testcommentimage1 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage2 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage3 = baker.make('devilry_comment.CommentFileImage')
        testcommentimage1.thumbnail.save('testfile.txt', ContentFile('test'))
        testcommentimage2.thumbnail = testcommentimage1.thumbnail
        testcommentimage2.full_clean()
        testcommentimage2.save()
        testcommentimage3.thumbnail = testcommentimage1.thumbnail
        testcommentimage3.full_clean()
        testcommentimage3.save()
        filepath = testcommentimage1.thumbnail.path
        self.assertTrue(os.path.exists(filepath))
        testcommentimage1.delete()
        self.assertTrue(os.path.exists(filepath))
        testcommentimage2.delete()
        self.assertTrue(os.path.exists(filepath))
        testcommentimage3.delete()
        self.assertFalse(os.path.exists(filepath))

    def test_delete_handles_image_not_set(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage',
                                      image='')
        testcommentimage.delete()  # No exception

    def test_delete_handles_thumbnail_not_set(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage',
                                      thumbnail='')
        testcommentimage.delete()  # No exception

    def test_delete_handles_image_does_not_exist_set(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage',
                                      image='')
        testcommentimage.image.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.image.path
        os.remove(filepath)
        testcommentimage.delete()  # No exception

    def test_delete_handles_thumbnail_does_not_exist_set(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage',
                                      thumbnail='')
        testcommentimage.thumbnail.save('testfile.txt', ContentFile('test'))
        filepath = testcommentimage.thumbnail.path
        os.remove(filepath)
        testcommentimage.delete()  # No exception

    def test_bulk_delete_removes_image(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage')
        testcommentimage.image.save('testfile.txt', ContentFile('test'))
        with self.assertRaisesMessage(
            NotImplementedError,
            'Bulk deletion not supported. Delete each CommentFileImage instead. '
            'This is because multiple CommentFileImages can point to the same FileField.path, '
            'and this check is handled in a pre_delete signal.'):
            CommentFileImage.objects.all().delete()

    def test_bulk_delete_removes_thumbnail(self):
        testcommentimage = baker.make('devilry_comment.CommentFileImage')
        testcommentimage.thumbnail.save('testfile.txt', ContentFile('test'))
        with self.assertRaisesMessage(
            NotImplementedError,
            'Bulk deletion not supported. Delete each CommentFileImage instead. '
            'This is because multiple CommentFileImages can point to the same FileField.path, '
            'and this check is handled in a pre_delete signal.'):
            CommentFileImage.objects.all().delete()
