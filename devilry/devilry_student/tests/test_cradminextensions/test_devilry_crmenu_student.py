import mock
from django import test
from model_bakery import baker

from devilry.devilry_student.cradminextensions import devilry_crmenu_student


class TestMenu(test.TestCase):
    def test_get_group_label(self):
        testgroup = baker.make('core.AssignmentGroup',
                               parentnode__short_name='testassignment')
        baker.make('core.Candidate', assignment_group=testgroup)
        mock_cradmin_instance = mock.MagicMock()
        menu = devilry_crmenu_student.Menu(cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            'testassignment',
            menu.get_group_label(group=testgroup))
