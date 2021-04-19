import mock
from django import test
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.devilry_examiner.cradminextensions import devilry_crmenu_examiner


class TestMenu(test.TestCase):
    def test_get_group_label_nonanonymous(self):
        testgroup = baker.make('core.AssignmentGroup')
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser',
                   relatedstudent__user__fullname='')
        mock_cradmin_instance = mock.MagicMock()
        menu = devilry_crmenu_examiner.Menu(cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            'testuser',
            menu.get_group_label(group=testgroup))

    def test_get_group_label_anonymous(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__anonymizationmode=Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)
        baker.make('core.Candidate',
                   assignment_group=testgroup,
                   relatedstudent__user__shortname='testuser',
                   relatedstudent__automatic_anonymous_id='secret')
        mock_cradmin_instance = mock.MagicMock()
        menu = devilry_crmenu_examiner.Menu(cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            'secret',
            menu.get_group_label(group=testgroup))
