from mock import patch
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.core.management import call_command
import haystack

from devilry_developer.testhelpers.corebuilder import PeriodBuilder
from devilry_developer.testhelpers.corebuilder import UserBuilder
from devilry_search.search_helper import SearchHelper


# @override_settings(
#     HAYSTACK_SEARCH_ENGINE = 'whoosh',
#     HAYSTACK_SITECONF = 'devilry_search.haystack_search_sites'
# )

HAYSTACK_SEARCH_ENGINE_TEST = 'whoosh'

@patch('haystack.backend', haystack.load_backend(HAYSTACK_SEARCH_ENGINE_TEST))
class TestSearchHelper(TestCase):
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.tempdir = mkdtemp()
        with self.whoosh_settings():
            self._clear_searchindex()

    def whoosh_settings(self):
        settings = {
            'HAYSTACK_SEARCH_ENGINE': HAYSTACK_SEARCH_ENGINE_TEST,
            'HAYSTACK_SITECONF': 'devilry_search.haystack_search_sites',
            'HAYSTACK_WHOOSH_PATH': join(self.tempdir, 'whoosh_index')
        }
        return self.settings(**settings)

    def tearDown(self):
        rmtree(self.tempdir)

    def _clear_searchindex(self):
        call_command('clear_index', verbosity=1, interactive=False)

    def _update_searchindex(self):
        haystack.autodiscover()
        call_command('update_index', verbosity=1, interactive=False)

    def test_get_student_results(self):
        with self.whoosh_settings():
            periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
            group1 = periodbuilder.add_assignment('assignment1', long_name="Assignment One")\
                .add_group().add_students(self.testuser).group
            group2 = periodbuilder.add_assignment('assignment2', long_name="Assignment Two")\
                .add_group().add_students(self.testuser).group
            group_not_student = periodbuilder.add_assignment('assignment3', long_name="Assignment Three")\
                .add_group().add_students(UserBuilder('nobody').user).group
            self._update_searchindex()
            results = SearchHelper(self.testuser, 'Assignment').get_student_results()
            self.assertEquals(results.count(), 2)
            self.assertEquals(set(map(lambda r: r.object, results)), set([group1, group2]))