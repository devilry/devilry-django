from __future__ import unicode_literals

from django import test
from django.db import IntegrityError

from model_mommy import mommy

from devilry.apps.core.models.period_tag import PeriodTag
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestPeriodTag(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_displayname_without_prefix(self):
        testperiodtag = mommy.make('core.PeriodTag', tag='a')
        self.assertEquals('a on {}'.format(testperiodtag.period), testperiodtag.displayname)

    def test_displayname_with_prefix(self):
        testperiodtag = mommy.make('core.PeriodTag', prefix='a', tag='b')
        self.assertEquals('a:b on {}'.format(testperiodtag.period), testperiodtag.displayname)

    def test_unique_together_without_prefix(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='a')
        with self.assertRaises(IntegrityError):
            mommy.make('core.PeriodTag', period=testperiod, tag='a')

    def test_unique_together_with_prefix(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='b')
        with self.assertRaises(IntegrityError):
            mommy.make('core.PeriodTag', period=testperiod, prefix='a', tag='b')

    def test_get_all_editable_tags(self):
        mommy.make('core.PeriodTag')
        mommy.make('core.PeriodTag')
        mommy.make('core.PeriodTag', prefix='a')
        mommy.make('core.PeriodTag', prefix='b')
        self.assertEquals(2, PeriodTag.objects.get_all_editable_tags().count())

    def test_auto_created_datetime(self):
        testperiodtag = mommy.make('core.PeriodTag')
        self.assertIsNotNone(testperiodtag.created_datetime)

    def test_add_relatedstudents(self):
        testperiodtag = mommy.make('core.PeriodTag')
        relatedstudent1 = mommy.make('core.RelatedStudent')
        relatedstudent2 = mommy.make('core.RelatedStudent')
        relatedstudent3 = mommy.make('core.RelatedStudent')
        testperiodtag.relatedstudents.add(relatedstudent1)
        testperiodtag.relatedstudents.add(relatedstudent2)
        testperiodtag.relatedstudents.add(relatedstudent3)
        self.assertEquals(3, PeriodTag.objects.get(id=testperiodtag.id).relatedstudents.count())

    def test_add_relatedexaminers(self):
        testperiodtag = mommy.make('core.PeriodTag')
        relatedexaminer1 = mommy.make('core.RelatedExaminer')
        relatedexaminer2 = mommy.make('core.RelatedExaminer')
        relatedexaminer3 = mommy.make('core.RelatedExaminer')
        testperiodtag.relatedexaminers.add(relatedexaminer1)
        testperiodtag.relatedexaminers.add(relatedexaminer2)
        testperiodtag.relatedexaminers.add(relatedexaminer3)
        self.assertEquals(3, PeriodTag.objects.get(id=testperiodtag.id).relatedexaminers.count())

    def test_add_relatedstudents_and_examiners(self):
        testperiodtag = mommy.make('core.PeriodTag')
        relatedexaminer1 = mommy.make('core.RelatedExaminer')
        relatedexaminer2 = mommy.make('core.RelatedExaminer')
        relatedexaminer3 = mommy.make('core.RelatedExaminer')
        testperiodtag.relatedexaminers.add(relatedexaminer1)
        testperiodtag.relatedexaminers.add(relatedexaminer2)
        testperiodtag.relatedexaminers.add(relatedexaminer3)
        relatedstudent1 = mommy.make('core.RelatedStudent')
        relatedstudent2 = mommy.make('core.RelatedStudent')
        relatedstudent3 = mommy.make('core.RelatedStudent')
        testperiodtag.relatedstudents.add(relatedstudent1)
        testperiodtag.relatedstudents.add(relatedstudent2)
        testperiodtag.relatedstudents.add(relatedstudent3)
        self.assertEquals(3, PeriodTag.objects.get(id=testperiodtag.id).relatedstudents.count())
        self.assertEquals(3, PeriodTag.objects.get(id=testperiodtag.id).relatedexaminers.count())

    def test_get_all_tags_on_period(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mommy.make('core.PeriodTag', period=testperiod, tag='b')
        mommy.make('core.PeriodTag', period=testperiod, tag='c')
        self.assertEquals(3, PeriodTag.objects.get_all_tags_on_period(period=testperiod).count())

    def test_get_all_distinct_tags(self):
        testperiod1 = mommy.make('core.Period')
        testperiod2 = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod1, tag='a')
        mommy.make('core.PeriodTag', period=testperiod1, tag='b')
        mommy.make('core.PeriodTag', period=testperiod2, tag='a')
        mommy.make('core.PeriodTag', period=testperiod2, tag='b')
        self.assertEquals(2, PeriodTag.objects.get_all_distinct_tags().count())
