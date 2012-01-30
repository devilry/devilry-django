from os.path import join
from unittest import TestCase
from devilry.utils.importutils import get_staticdir_from_appname


class TestImportUtils(TestCase):
    def test_get_staticdir_from_appname(self):
        staticdir = get_staticdir_from_appname('test',
                                               [(join('path', 'to'), None, 'something'),
                                                (join('another', 'dir'), None, 'test')])
        self.assertEquals(staticdir, join('another', 'dir', 'static', 'test'))
        self.assertRaises(ValueError, get_staticdir_from_appname, 'test', [])
