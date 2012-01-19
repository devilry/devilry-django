from django.test import TestCase
import i18n
import utils


class TestI18n(TestCase):
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


class TestUtils(TestCase):
    def test_get_languagecode(self):
        self.assertEquals(utils.get_languagecode('en-US,en;q=0.8', {'en-US': ''}),
                          'en-US')
        self.assertEquals(utils.get_languagecode('en-US,en;q=0.8', {'en': ''}),
                          'en')
        self.assertEquals(utils.get_languagecode('en-US,en;q=0.8', {'no-NB': ''}),
                          None)
        self.assertEquals(utils.get_languagecode('en-US,en;q=0.4,no-NB,no;q=0.8', {'no': '', 'en-US': ''}),
                          'en-US')
        self.assertEquals(utils.get_languagecode('en-US,en;q=0.4,no-NB,no;q=0.8', {'no': '', 'en': ''}),
                          'no')

    #def test_get_languagecode(self):
        #self.assertEquals(utils.get_languagecode('en-US,en;q=0.8', {'en-US': ''}),
                          #'en-US')
