import mock
from django import test
from model_mommy import mommy

from devilry.devilry_examiner.cradminextensions import devilry_crmenu_examiner


class TestMenu(test.TestCase):
    def test_get_group_label_no_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mock_cradmin_instance = mock.MagicMock()
        menu = devilry_crmenu_examiner.Menu(cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            '#{}'.format(testgroup.id),
            menu.get_group_label(group=testgroup))

    def test_get_group_label_nonanonymous_fullname(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser',
                   relatedstudent__user__fullname='Test User')
        mock_cradmin_instance = mock.MagicMock()
        menu = devilry_crmenu_examiner.Menu(cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            'Test User',
            menu.get_group_label(group=testgroup))

    def test_get_group_label_nonanonymous_shortname(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser',
                   relatedstudent__user__fullname='')
        mock_cradmin_instance = mock.MagicMock()
        menu = devilry_crmenu_examiner.Menu(cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            'testuser',
            menu.get_group_label(group=testgroup))

    def test_get_group_label_nonanonymous_multiple_candidates(self):
        testgroup = mommy.make('core.AssignmentGroup')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testusera',
                   relatedstudent__user__fullname='A Test User')
        mommy.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuserb',
                   relatedstudent__user__fullname='')
        mock_cradmin_instance = mock.MagicMock()
        menu = devilry_crmenu_examiner.Menu(cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            {'A Test User', 'testuserb'},
            set(menu.get_group_label(group=testgroup).split(', ')))
