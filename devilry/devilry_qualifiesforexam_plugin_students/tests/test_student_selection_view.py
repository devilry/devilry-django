# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# 3rd party imports
from model_mommy import mommy

# CrAdmin imports
from django_cradmin import cradmin_testhelpers

# Django imports
from django import test

# Devilry imports
from devilry.devilry_qualifiesforexam_plugin_students.views import select_students


class TestStudentSelectionView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = select_students.PluginSelectStudentsView

    def test_elements_are_listed(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        mommy.make('core.RelatedStudent', period=testperiod, _quantity=20)

        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEquals(len(mockresponse.selector.list('.django-cradmin-listbuilder-itemvalue')), 20)

    def test_all_students_are_listed(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        relatedstudents = mommy.make('core.RelatedStudent', period=testperiod, _quantity=20)

        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        selectorlist = mockresponse.selector.list(
                '.django-cradmin-listbuilder-itemvalue-titledescription-title'
        )
        elements_normalized = [element.alltext_normalized for element in selectorlist]
        self.assertEquals(len(elements_normalized), len(relatedstudents))
        for relatedstudent in relatedstudents:
            self.assertIn(relatedstudent.__unicode__(), elements_normalized)
