import mock
from django.contrib import messages
from django.test import TestCase
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import Assignment
from devilry.devilry_admin.views.assignment import anonymizationmode


class TestAssignmentAnonymizationmodeUpdateView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = anonymizationmode.AssignmentAnonymizationmodeUpdateView

    def test_get_h1(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk':assignment.id})
        self.assertEqual(mockresponse.selector.one('h1').alltext_normalized,
                          'Edit anonymization settings')

    def test_get_anonymizationmode_choices_sanity(self):
        assignment = baker.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        self.assertEqual(
            mockresponse.selector.count('input[name="anonymizationmode"]'),
            2)

    def test_get_anonymizationmode_labels(self):
        assignment = baker.make_recipe('devilry.apps.core.assignment_activeperiod_start')
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=assignment, viewkwargs={'pk': assignment.id})
        labels = [element.alltext_normalized
                  for element in mockresponse.selector.list('#div_id_anonymizationmode .radio label')]
        self.assertEqual(len(labels), 2)
        self.assertTrue(labels[0].startswith('OFF.'))
        self.assertTrue(labels[1].startswith('SEMI ANONYMOUS.'))

    def test_post_sanity(self):
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        self.mock_http302_postrequest(
            cradmin_role=assignment,
            viewkwargs={'pk': assignment.id},
            requestkwargs={'data': {'anonymizationmode': Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS}})
        assignment.refresh_from_db()
        self.assertEqual(assignment.anonymizationmode,
                         Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS)

    def test_post_success_message(self):
        assignment = baker.make_recipe(
            'devilry.apps.core.assignment_activeperiod_start',
            anonymizationmode=Assignment.ANONYMIZATIONMODE_OFF)
        messagesmock = mock.MagicMock()
        self.mock_http302_postrequest(
            cradmin_role=assignment,
            viewkwargs={'pk': assignment.id},
            requestkwargs={'data': {
                'anonymizationmode': Assignment.ANONYMIZATIONMODE_SEMI_ANONYMOUS
            }},
            messagesmock=messagesmock)
        messagesmock.add.assert_called_once_with(
            messages.SUCCESS,
            'Changed anonymization mode from "off" to "semi anonymous".',
            '')
