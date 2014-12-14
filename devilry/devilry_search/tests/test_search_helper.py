import unittest
from mock import patch
from tempfile import mkdtemp
from shutil import rmtree
from os.path import join
from django.test import TestCase
from django.core.management import call_command
import haystack

from devilry.project.develop.testhelpers.corebuilder import NodeBuilder
from devilry.project.develop.testhelpers.corebuilder import PeriodBuilder
from devilry.project.develop.testhelpers.corebuilder import UserBuilder
from devilry.devilry_search.search_helper import SearchHelper


HAYSTACK_SEARCH_ENGINE_TEST = 'whoosh'


@unittest.skip
class TestSearchHelper(TestCase):
    """

    WARNING: These tests has be run one at a time to avoid a MAIN_WRITELOCK not found error.
    Not really a problem because these tests should not be run by Travis, and we should fix
    this when updating to haystack2.

    """
    def setUp(self):
        self.testuser = UserBuilder('testuser').user
        self.tempdir = mkdtemp()

    def _whoosh_settings(self):
        settings = {
            'HAYSTACK_SEARCH_ENGINE': HAYSTACK_SEARCH_ENGINE_TEST,
            'HAYSTACK_WHOOSH_PATH': join(self.tempdir, 'whoosh_index')
        }
        return self.settings(**settings)

    def tearDown(self):
        rmtree(self.tempdir)


    def _rebuild_searchindex(self):
        haystack.autodiscover()
        call_command('rebuild_index', verbosity=1, interactive=False)

    def test_get_student_results(self):
        backend = haystack.load_backend(HAYSTACK_SEARCH_ENGINE_TEST)
        with self._whoosh_settings():
            with patch('haystack.backend', backend):
                periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
                group1 = periodbuilder.add_assignment('assignment1', long_name="Assignment One")\
                    .add_group().add_students(self.testuser).group
                group2 = periodbuilder.add_assignment('assignment2', long_name="Assignment Two")\
                    .add_group().add_students(self.testuser).group
                group_not_student = periodbuilder.add_assignment('assignment3', long_name="Assignment Three")\
                    .add_group().add_students(UserBuilder('nobody').user).group
                self._rebuild_searchindex()
                results = SearchHelper(self.testuser, 'Assignment').get_student_results()
                self.assertEquals(results.count(), 2)
                self.assertEquals(set(map(lambda r: r.object, results)), set([group1, group2]))

    def test_get_examiner_results(self):
        with self._whoosh_settings():
            with patch('haystack.backend', haystack.load_backend(HAYSTACK_SEARCH_ENGINE_TEST)):
                periodbuilder = PeriodBuilder.quickadd_ducku_duck1010_active()
                assignment1builder = periodbuilder.add_assignment('assignment1', long_name="Assignment One")
                assignment2builder = periodbuilder.add_assignment('assignment2', long_name="Assignment Two")
                group1 = assignment1builder.add_group().add_examiners(self.testuser).group
                group2 = assignment1builder.add_group().add_examiners(self.testuser).group
                group3 = assignment2builder.add_group().add_examiners(self.testuser).group
                assignment2builder.add_group().add_examiners(UserBuilder('nobody').user) # Should not math
                self._rebuild_searchindex()
                results = SearchHelper(self.testuser, 'Assignment').get_examiner_results()
                self.assertEquals(results.count(), 5)
                self.assertEquals(set(map(lambda r: r.object, results)),
                    set([group1, group2, group3,
                        assignment1builder.assignment, assignment2builder.assignment]))


    def test_get_admin_results(self):
        with self._whoosh_settings():
            with patch('haystack.backend', haystack.load_backend(HAYSTACK_SEARCH_ENGINE_TEST)):
                rootnodebuilder = NodeBuilder('rootnode', 'Test Roonode')

                # We should match all subjects, periods, assignments and groups in node1 - we are admin on the node
                node1builder = rootnodebuilder\
                    .add_childnode('node1', 'Test Node One').add_admins(self.testuser)
                subject1builder = node1builder.add_subject('subject1', 'Test Subject One')
                period1builder = subject1builder.add_6month_active_period(
                    short_name='period1',
                    long_name='Test Period One')
                assignment1builder = period1builder.add_assignment('test1', long_name="Test Assignment One")
                group1builder = assignment1builder.add_group()

                # We should only match the assignment and the group in node2 - we are only admin on assignment1
                node2builder = rootnodebuilder\
                    .add_childnode('node2', 'Test Node Two')
                assignment2builder = node2builder\
                    .add_subject('subject2', 'Test Subject Two')\
                    .add_6month_active_period(
                        short_name='period2',
                        long_name='Test Period Two')\
                    .add_assignment('test2', long_name="Test Assignment One")\
                        .add_admins(self.testuser)
                group2builder = assignment2builder.add_group()

                self._rebuild_searchindex()
                results = SearchHelper(self.testuser, 'Test').get_admin_results()
                self.assertEquals(set(map(lambda r: r.object, results)), set([
                    node1builder.node,
                    subject1builder.subject,
                    period1builder.period,
                    assignment1builder.assignment,
                    group1builder.group,
                    assignment2builder.assignment,
                    group2builder.group,
                ]))


    def test_get_admin_results_superuser(self):
        with self._whoosh_settings():
            with patch('haystack.backend', haystack.load_backend(HAYSTACK_SEARCH_ENGINE_TEST)):
                testsuperuser = UserBuilder('testsuperuser', is_superuser=True).user

                # We should match all subjects, periods, assignments and groups - we are superuser
                rootnodebuilder = NodeBuilder('rootnode', 'Test Roonode')
                node1builder = rootnodebuilder\
                    .add_childnode('node1', 'Test Node One').add_admins(self.testuser)
                subject1builder = node1builder.add_subject('subject1', 'Test Subject One')
                period1builder = subject1builder.add_6month_active_period(
                    short_name='period1',
                    long_name='Test Period One')
                assignment1builder = period1builder.add_assignment('test1', long_name="Test Assignment One")
                group1builder = assignment1builder.add_group()

                self._rebuild_searchindex()
                results = SearchHelper(testsuperuser, 'Test').get_admin_results()
                self.assertEquals(set(map(lambda r: r.object, results)), set([
                    rootnodebuilder.node,
                    node1builder.node,
                    subject1builder.subject,
                    period1builder.period,
                    assignment1builder.assignment,
                    group1builder.group,
                ]))
