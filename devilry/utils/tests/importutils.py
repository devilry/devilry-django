import unittest
from os.path import join
from unittest import TestCase

from devilry.utils.importutils import get_staticdir_from_appname


@unittest.skip('Is this in use? If so TestImportUtils should be fixed.')
class TestImportUtils(TestCase):
    def test_get_staticdir_from_appname(self):
        staticdir = get_staticdir_from_appname('test',
                                               [(join('path', 'to'), None, 'something'),
                                                (join('another', 'dir'), None, 'test')])
        self.assertEqual(staticdir, join('another', 'dir', 'static', 'test'))
        self.assertRaises(ValueError, get_staticdir_from_appname, 'test', [])
