import mock
from django import test
from django.conf import settings

from model_bakery import baker
from cradmin_legacy import cradmin_testhelpers

from devilry.devilry_admin.views.dashboard.student_feedbackfeed_wizard import student_list


class TestStudentListView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = student_list.UserListView

    def test_title(self):
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertEqual(mockresponse.selector.one('title').alltext_normalized, 'Select a student')

    def test_only_users_with_relatedstudent_are_listed(self):
        baker.make(settings.AUTH_USER_MODEL, shortname='notstudentuser')
        baker.make('core.RelatedStudent', user__shortname='studentuser')
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue-titledescription-title'), 1)
        self.assertContains(mockresponse.response, 'studentuser')
        self.assertNotContains(mockresponse.response,'notstudentuser')

    def test_list_users(self):
        baker.make('core.RelatedStudent', user__shortname='a', user__fullname='A')
        baker.make('core.RelatedStudent', user__shortname='b', user__fullname='B')
        baker.make('core.RelatedStudent', user__shortname='c', user__fullname='C')
        mockresponse = self.mock_http200_getrequest_htmls()
        fullname_list = [element.alltext_normalized for element in mockresponse.selector.list(
            '.cradmin-legacy-listbuilder-itemvalue-titledescription-title')]
        shortname_list = [element.alltext_normalized for element in mockresponse.selector.list(
            '.cradmin-legacy-listbuilder-itemvalue-titledescription-description')]
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 3)
        self.assertIn('A', fullname_list)
        self.assertIn('B', fullname_list)
        self.assertIn('C', fullname_list)
        self.assertIn('a', shortname_list)
        self.assertIn('b', shortname_list)
        self.assertIn('c', shortname_list)

    def test_search_no_match(self):
        baker.make('core.RelatedStudent', user__shortname='a', user__fullname='A')
        mockresponse = self.mock_http200_getrequest_htmls(
            viewkwargs={'filters_string': 'search-No match'}
        )
        self.assertEqual(0, mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_search_match_fullname(self):
        baker.make('core.RelatedStudent', user__shortname='shortnamea', user__fullname='FullnameA')
        mockresponse = self.mock_http200_getrequest_htmls(
            viewkwargs={'filters_string': 'search-FullnameA'}
        )
        self.assertEqual(1, mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_search_match_shortname(self):
        baker.make('core.RelatedStudent', user__shortname='shortnamea', user__fullname='FullnameA')
        mockresponse = self.mock_http200_getrequest_htmls(
            viewkwargs={'filters_string': 'search-shortnamea'}
        )
        self.assertEqual(1, mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'))

    def test_backlink(self):
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertEqual(1, len(mockresponse.request.cradmin_instance.reverse_url.call_args_list))
        self.assertEqual(
            mock.call(appname='overview', args=(), kwargs={}, viewname='INDEX'),
            mockresponse.request.cradmin_instance.reverse_url.call_args_list[0]
        )

    def test_pagination(self):
        baker.make('core.RelatedStudent', _quantity=50)
        mockresponse = self.mock_http200_getrequest_htmls()
        self.assertEqual(mockresponse.selector.count('.cradmin-legacy-listbuilder-itemvalue'), 35)

    def test_query_count(self):
        baker.make('core.RelatedStudent', _quantity=10)
        with self.assertNumQueries(5):
            self.mock_http200_getrequest_htmls()
        baker.make('core.RelatedStudent', _quantity=90)
        with self.assertNumQueries(5):
            self.mock_http200_getrequest_htmls()
        baker.make('core.RelatedStudent', _quantity=400)
        with self.assertNumQueries(5):
            self.mock_http200_getrequest_htmls()
