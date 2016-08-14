from django.db import IntegrityError
from django.test import TestCase
from model_mommy import mommy


class TestCompressedFileMeta(TestCase):

    def test_get_full_path(self):
        archivemeta = mommy.make('devilry_ziputil.CompressedFileMeta',
                                 archive_name='test.zip',
                                 archive_path='path/to/archive')
        self.assertTrue('path/to/archive/test.zip', archivemeta.get_full_path())

    def test_generic_foreignkey_comment(self):
        testcomment = mommy.make('devilry_comment.Comment')
        archivemeta = mommy.make('devilry_ziputil.CompressedFileMeta', content_object=testcomment)
        self.assertEquals(archivemeta.content_object_id, testcomment.id)
        self.assertEquals(type(archivemeta.content_object), type(testcomment))

    def test_unique_constraint(self):
        testcomment = mommy.make('devilry_comment.Comment')
        mommy.make('devilry_ziputil.CompressedFileMeta', content_object=testcomment)

        with self.assertRaises(IntegrityError):
            mommy.make('devilry_ziputil.CompressedFileMeta', content_object=testcomment)
