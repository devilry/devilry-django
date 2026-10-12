from django.test import TestCase
from cradmin_legacy.utils import crhumanize


class TestHumanReadableFileSize(TestCase):
    def test_less_than_kb(self):
        self.assertEqual("0B", crhumanize.human_readable_filesize(0))
        self.assertEqual("999B", crhumanize.human_readable_filesize(999))

    def test_kb(self):
        self.assertEqual("1KB", crhumanize.human_readable_filesize(1000))
        self.assertEqual("999KB", crhumanize.human_readable_filesize(999999))

    def test_mb(self):
        self.assertEqual("1.0MB", crhumanize.human_readable_filesize(1000000))
        self.assertEqual("55.6MB", crhumanize.human_readable_filesize(55555555))

    def test_gb(self):
        self.assertEqual("1.00GB", crhumanize.human_readable_filesize(1000000000))
        self.assertEqual("55.56GB", crhumanize.human_readable_filesize(55555555555))

    def test_tb(self):
        self.assertEqual("1.00TB", crhumanize.human_readable_filesize(1000000000000))
        self.assertEqual("55.56TB", crhumanize.human_readable_filesize(55555555555555))


class TestDehumanizeReadableFileSize(TestCase):
    def test_less_than_kb(self):
        self.assertEqual(0, crhumanize.dehumanize_readable_filesize("0B"))
        self.assertEqual(999, crhumanize.dehumanize_readable_filesize("999B"))

    def test_kb(self):
        self.assertEqual(1000, crhumanize.dehumanize_readable_filesize("1KB"))
        self.assertEqual(999000, crhumanize.dehumanize_readable_filesize("999KB"))

    def test_mb(self):
        self.assertEqual(1000000, crhumanize.dehumanize_readable_filesize("1.0MB"))
        self.assertEqual(55600000, crhumanize.dehumanize_readable_filesize("55.6MB"))

    def test_gb(self):
        self.assertEqual(1000000000, crhumanize.dehumanize_readable_filesize("1.00GB"))
        self.assertEqual(55560000000, crhumanize.dehumanize_readable_filesize("55.56GB"))

    def test_tb(self):
        self.assertEqual(1000000000000, crhumanize.dehumanize_readable_filesize("1.00TB"))
        self.assertEqual(55560000000000, crhumanize.dehumanize_readable_filesize("55.56TB"))
