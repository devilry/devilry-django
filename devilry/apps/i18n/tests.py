from django.test import TestCase
import i18n
import utils


class TestDecoupleFlattened(TestCase):
    def setUp(self):
        self.loader = i18n.Loader()

    def test_decoupleflattened(self):
        indata = {'core.assignment': 'Oppgave',
                  'core.period': 'Period', # Same value as default
                  'core.subject': 'Kurs',
                  'doesnotexist': 'Does not exists' # Does not exist in default
                 }
        decoupled = i18n.DecoupleFlattened(self.loader, indata)
        self.assertEquals(decoupled.result, {'core': {'core.assignment': 'Oppgave', 'core.subject': 'Kurs'}})


class TestFlatten(TestCase):
    class MochLoader(object):
        def iterdata(self):
            yield 'core', '/core/i18ndir', {'core.node': 'Node', 'core.assignment': 'Assignment'}
            yield 'example', '/example/i18ndir', {'example.tst': 'Test'}

    class MochFlatten(i18n.Flatten):
        def __init__(self):
            self.saved_filenames = []
            self.saved_filecontents = []
            super(TestFlatten.MochFlatten, self).__init__(TestFlatten.MochLoader())

        def _listdir(self, i18ndir):
            return []

        def _read_messagesfile(self, messagesfile):
            return None

        def _create_exportdir(self, exportdir):
            pass

        def _get_exportddir(self):
            return '/exportdir'
        def _savefile(self, filename, content):
            self.saved_filenames.append(filename)
            self.saved_filecontents.append(content)
            self.last_written_content = content
            self.last_written_filename = filename

    def test_save_js(self):
        flatten = self.MochFlatten()
        flatten._save_js('/export', 'somename', 'DUMMY')
        self.assertEquals(flatten.last_written_filename, '/export/somename.js')
        self.assertEquals(flatten.last_written_content.strip(), "var i18n = DUMMY;")

    def test_save_json(self):
        flatten = self.MochFlatten()
        flatten._save_json('/export', 'somename', 'DUMMY')
        self.assertEquals(flatten.last_written_filename, '/export/somename.json')
        self.assertEquals(flatten.last_written_content.strip(), "DUMMY")

    def test_save_index(self):
        flatten = self.MochFlatten()
        flatten._save_index('/export', ['a', 'b'])
        self.assertEquals(flatten.last_written_filename, '/export/index.json')
        self.assertEquals(flatten.last_written_content.strip(), '["a", "b"]')

    def test_save(self):
        flatten = self.MochFlatten()
        flatten.save()
        print flatten.saved_filecontents
        self.assertEquals(flatten.saved_filenames,
                          ['/exportdir/messages.js', '/exportdir/messages.json', '/exportdir/index.json'])
        self.assertEquals(len(flatten.saved_filecontents), 3)
        self.assertEquals(flatten.saved_filecontents[-1],
                          '["messages"]')


class TestUtils(TestCase):
    def test_get_languagecode(self):
        self.assertEquals(utils.get_languagecode_from_httpheader('en-US,en;q=0.8', {'en-US': ''}),
                          'en-US')
        self.assertEquals(utils.get_languagecode_from_httpheader('en-US,en;q=0.8', {'en': ''}),
                          'en')
        self.assertEquals(utils.get_languagecode_from_httpheader('en-US,en;q=0.8', {'no-NB': ''}),
                          None)
        self.assertEquals(utils.get_languagecode_from_httpheader('en-US,en;q=0.4,no-NB,no;q=0.8', {'no': '', 'en-US': ''}),
                          'en-US')
        self.assertEquals(utils.get_languagecode_from_httpheader('en-US,en;q=0.4,no-NB,no;q=0.8', {'no': '', 'en': ''}),
                          'no')

    #def test_get_languagecode(self):
        #self.assertEquals(utils.get_languagecode_from_httpheader('en-US,en;q=0.8', {'en-US': ''}),
                          #'en-US')
