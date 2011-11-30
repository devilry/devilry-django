from django.test import TestCase
import i18n


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
