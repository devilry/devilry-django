import datetime
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
