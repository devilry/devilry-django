import datetime

import htmls
import mock
from django.test import TestCase
from django_cradmin import cradmin_testhelpers
from model_mommy import mommy

from devilry.apps.core.mommy_recipes import ACTIVE_PERIOD_START
from devilry.devilry_admin.views.assignment.students import create_groups


class TestChooseMethod(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = create_groups.ChooseMethod

    def test_title(self):
        testassignment = mommy.make('core.Assignment',
                                    short_name='testassignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertIn(
            'Add students to testsubject.testperiod.testassignment',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Add students',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_choices_sanity(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            2,
            mockresponse.selector.count('select#id_method option'))

    def test_choice_all_value(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'all-from-period',
            mockresponse.selector.one('select#id_method option:first-child')['value'])

    def test_choice_all_label(self):
        testassignment = mommy.make('core.Assignment',
                                    parentnode__parentnode__short_name='testsubject',
                                    parentnode__short_name='testperiod')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'All students registered on testsubject.testperiod',
            mockresponse.selector.one('select#id_method option:first-child').alltext_normalized)

    def test_choice_select_manually_value(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'select-manually',
            mockresponse.selector.one('select#id_method option:last-child')['value'])

    def test_choice_select_manually_label(self):
        testassignment = mommy.make('core.Assignment')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Select manually',
            mockresponse.selector.one('select#id_method option:last-child').alltext_normalized)

    def test_choices_does_not_include_current_assignment(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.Assignment', parentnode=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            4,
            mockresponse.selector.count('select#id_method option'))
        self.assertFalse(
            mockresponse.selector.exists('select#id_method option[value="copy-passing-from-assignment-{}"]'.format(
                    testassignment.pk)))
        self.assertFalse(
            mockresponse.selector.exists('select#id_method option[value="copy-all-from-assignment-{}"]'.format(
                    testassignment.pk)))

    def test_other_assignment_rending(self):
        testperiod = mommy.make('core.Period')
        otherassignment = mommy.make('core.Assignment', parentnode=testperiod,
                                     long_name='Other Assignment')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Students with passing grade on Other Assignment',
            mockresponse.selector.one('select#id_method option[value="copy-passing-from-assignment-{}"]'.format(
                    otherassignment.pk)).alltext_normalized)
        self.assertEqual(
            'All students registered on Other Assignment',
            mockresponse.selector.one('select#id_method option[value="copy-all-from-assignment-{}"]'.format(
                    otherassignment.pk)).alltext_normalized)

    def test_other_assignments_ordering(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make('core.Assignment', parentnode=testperiod,
                   long_name='Assignment 1',
                   publishing_time=ACTIVE_PERIOD_START + datetime.timedelta(days=1))
        mommy.make('core.Assignment', parentnode=testperiod,
                   long_name='Assignment 2',
                   publishing_time=ACTIVE_PERIOD_START + datetime.timedelta(days=2))
        mommy.make('core.Assignment', parentnode=testperiod,
                   long_name='Assignment 3',
                   publishing_time=ACTIVE_PERIOD_START + datetime.timedelta(days=3))
        assignment4 = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=assignment4)
        optgroup_labels = [optgroup['label']
                           for optgroup in mockresponse.selector.list('select#id_method optgroup')]
        self.assertEqual(
            [
                'Copy from Assignment 3',
                'Copy from Assignment 2',
                'Copy from Assignment 1',
            ],
            optgroup_labels
        )


class TestRelatedStudentMultiselectTarget(TestCase):
    def test_with_items_title(self):
        selector = htmls.S(create_groups.RelatedStudentMultiselectTarget().render(request=mock.MagicMock()))
        self.assertEqual(
            'Add students',
            selector.one('button[type="submit"]').alltext_normalized)


class TestManualSelectStudentsView(TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = create_groups.ManualSelectStudentsView

    def test_title(self):
        testassignment = mommy.make('core.Assignment',
                                    short_name='testassignment',
                                    parentnode__short_name='testperiod',
                                    parentnode__parentnode__short_name='testsubject')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertIn(
            'Select the students you want to add to testsubject.testperiod.testassignment',
            mockresponse.selector.one('title').alltext_normalized)

    def test_h1(self):
        testassignment = mommy.make('core.Assignment', long_name='Assignment One')
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Select the students you want to add to Assignment One',
            mockresponse.selector.one('h1').alltext_normalized)

    def test_no_relatedstudents(self):
        testperiod = mommy.make('core.Period')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'No students found.',
            mockresponse.selector.one(
                    '.devilry-admin-create-groups-manual-select-no-relatedstudents-message').alltext_normalized)

    def test_relatedstudent_not_in_assignment_period_excluded(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent')
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_relatedstudent_in_assignment_period_included(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_relatedstudent_with_candidate_on_assignment_not_included(self):
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mommy.make('core.Candidate',
                   relatedstudent=relatedstudent,
                   assignment_group__parentnode=testassignment)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            0,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))

    def test_render_relatedstudent_sanity(self):
        # This is tested in detail in the tests for
        # devilry.devilry_admin.cradminextensions.multiselect2.multiselect2_relatedstudent.ItemValue
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   user__fullname='Test User',
                   period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testassignment)
        self.assertEqual(
            'Test User',
            mockresponse.selector.one('.django-cradmin-multiselect2-itemvalue-title').alltext_normalized)

    def test_render_search(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   user__fullname='Match User',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__fullname='Other User',
                   period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'search-match'}
        )
        self.assertEqual(
            1,
            mockresponse.selector.count('.django-cradmin-listbuilder-itemvalue'))
        self.assertEqual(
            'Match User',
            mockresponse.selector.one('.django-cradmin-multiselect2-itemvalue-title').alltext_normalized)

    def test_render_orderby_default(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   user__fullname='userb@example.com',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__fullname='UserA',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__fullname='userc',
                   period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment)
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list('.django-cradmin-multiselect2-itemvalue-title')]
        self.assertEqual(
            ['UserA', 'userb@example.com', 'userc'],
            titles)

    def test_render_orderby_name_descending(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__fullname='UserA',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__fullname='userc',
                   period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-name_descending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list('.django-cradmin-multiselect2-itemvalue-title')]
        self.assertEqual(
            ['userc', 'userb@example.com', 'UserA'],
            titles)

    def test_render_orderby_lastname_ascending(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__fullname='User Aaa',
                   user__lastname='Aaa',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__fullname='User ccc',
                   user__lastname='ccc',
                   period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-lastname_ascending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list('.django-cradmin-multiselect2-itemvalue-title')]
        self.assertEqual(
            ['userb@example.com', 'User Aaa', 'User ccc'],
            titles)

    def test_render_orderby_lastname_descending(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__fullname='User Aaa',
                   user__lastname='Aaa',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__fullname='User ccc',
                   user__lastname='ccc',
                   period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-lastname_descending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list('.django-cradmin-multiselect2-itemvalue-title')]
        self.assertEqual(
            ['User ccc', 'User Aaa', 'userb@example.com'],
            titles)

    def test_render_orderby_shortname_ascending(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__shortname='usera@example.com',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__shortname='userc@example.com',
                   period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-shortname_ascending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list('.django-cradmin-multiselect2-itemvalue-title')]
        self.assertEqual(
            ['usera@example.com', 'userb@example.com', 'userc@example.com'],
            titles)

    def test_render_orderby_shortname_descending(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.RelatedStudent',
                   user__shortname='userb@example.com',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__shortname='usera@example.com',
                   period=testperiod)
        mommy.make('core.RelatedStudent',
                   user__shortname='userc@example.com',
                   period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http200_getrequest_htmls(
            cradmin_role=testassignment,
            viewkwargs={'filters_string': 'orderby-shortname_descending'})
        titles = [element.alltext_normalized
                  for element in mockresponse.selector.list('.django-cradmin-multiselect2-itemvalue-title')]
        self.assertEqual(
            ['userc@example.com', 'userb@example.com', 'usera@example.com'],
            titles)

    def test_post_ok(self):
        testperiod = mommy.make('core.Period')
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__shortname='userb@example.com',
                                    period=testperiod)
        testassignment = mommy.make('core.Assignment', parentnode=testperiod)
        mockresponse = self.mock_http302_postrequest(
            cradmin_role=testassignment,
            requestkwargs={
                'data': {
                    'selected_related_students': [
                        relatedstudent.id
                    ]
                }
            }
        )
