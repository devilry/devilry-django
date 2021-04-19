# -*- coding: utf-8 -*-


# 3rd party imports
from model_bakery import baker

# CrAdmin imports
from cradmin_legacy import cradmin_testhelpers

# Django imports
from django import test

# Devilry imports
from devilry.devilry_qualifiesforexam_plugin_students.views import select_students


class TestStudentSelectionView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = select_students.PluginSelectStudentsView

    def test_elements_are_listed(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        baker.make('core.RelatedStudent', period=testperiod, _quantity=20)

        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        self.assertEqual(len(mockresponse.selector.list('.cradmin-legacy-listbuilder-itemvalue')), 20)

    def test_all_students_are_listed(self):
        testperiod = baker.make_recipe('devilry.apps.core.period_active')
        relatedstudents = baker.make('core.RelatedStudent', period=testperiod, _quantity=20)

        mockresponse = self.mock_http200_getrequest_htmls(cradmin_role=testperiod)
        selectorlist = mockresponse.selector.list(
                '.cradmin-legacy-listbuilder-itemvalue-titledescription-description'
        )
        elements_normalized = [element.alltext_normalized for element in selectorlist]
        self.assertEqual(len(elements_normalized), len(relatedstudents))
        for relatedstudent in relatedstudents:
            self.assertIn(relatedstudent.user.shortname, elements_normalized)
