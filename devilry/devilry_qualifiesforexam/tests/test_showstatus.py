# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# 3rd party imports
from model_mommy import mommy

# Django imports
from django import test

# CrAdmin imports
from django_cradmin import cradmin_testhelpers

# Devilry imports
from devilry.project.common import settings
from devilry.devilry_qualifiesforexam.views import qualification_preview_view
from devilry.devilry_qualifiesforexam import models as status_models


class TestQualificationStatusView(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = qualification_preview_view.QualificationStatusPreview

    def test_get(self):
        testperiod = mommy.make_recipe('devilry.apps.core.period_active')
        admin_user = mommy.make(settings.AUTH_USER_MODEL)
        teststatus = mommy.make('devilry_qualifiesforexam.Status',
                                period=testperiod,
                                status=status_models.Status.READY,
                                user=admin_user,
                                plugin='someplugin')
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   qualifies=True,
                   relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   qualifies=True,
                   relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   qualifies=True,
                   relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
                   status=teststatus,
                   qualifies=True,
                   relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        # mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
        #            status=teststatus,
        #            qualifies=True,
        #            relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        # mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
        #            status=teststatus,
        #            qualifies=True,
        #            relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        # mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
        #            status=teststatus,
        #            qualifies=True,
        #            relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        # mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
        #            status=teststatus,
        #            qualifies=True,
        #            relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        # mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
        #            status=teststatus,
        #            qualifies=True,
        #            relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        # mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
        #            status=teststatus,
        #            qualifies=True,
        #            relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        # mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
        #            status=teststatus,
        #            qualifies=True,
        #            relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        # mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
        #            status=teststatus,
        #            qualifies=True,
        #            relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))
        # mommy.make('devilry_qualifiesforexam.QualifiesForFinalExam',
        #            status=teststatus,
        #            qualifies=True,
        #            relatedstudent=mommy.make('core.RelatedStudent', period=testperiod))

        with self.assertNumQueries(4):
            mockresponse = self.mock_http200_getrequest_htmls(
                    cradmin_role=testperiod,
                    requestuser=admin_user
            )
            # mockresponse.selector.prettyprint()
