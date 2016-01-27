import mock
from django import test
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.devilry_admin.views.assignment.examiners import bulk_organize


class TestSelectMethodView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = bulk_organize.SelectMethodView

    def test_title(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertIn(
            'How would you like to bulk-organize your examiners?',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment', long_name='Test Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'How would you like to bulk-organize your examiners?',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_buttons_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            1,
            mockresponse.selector.count(
                '#devilry_admin_assignment_examiners_bulk_organize_buttons .btn'))

    def test_buttonbar_organize_examiners_link(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mock_cradmin_instance = mock.MagicMock()

        def mock_reverse_url(appname, viewname, **kwargs):
            return '/{}/{}'.format(appname, viewname)

        mock_cradmin_instance.reverse_url = mock_reverse_url
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            cradmin_instance=mock_cradmin_instance)
        self.assertEqual(
            # '/bulk_organize_examiners/INDEX',
            '#',
            mockresponse.selector
            .one('#devilry_admin_assignment_examiners_bulk_organize_button_random')['href'])

    def test_buttonbar_organize_examiners_text(self):
        testassignment = mommy.make('core.Assignment')
        mommy.make('core.RelatedExaminer', period=testassignment.period)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Organize examiners randomly( Select students and '
            'randomly assign two or more examiners to those students )',
            mockresponse.selector
            .one('#devilry_admin_assignment_examiners_bulk_organize_button_random')
            .alltext_normalized)
