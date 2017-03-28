from __future__ import unicode_literals

from django import test
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings

from model_mommy import mommy

from devilry.apps.core.models.period_tag import PeriodTag
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestPeriodTag(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_full_clean_tag_cannot_be_blank(self):
        with self.assertRaises(ValidationError):
            mommy.make('core.PeriodTag', tag='').full_clean()

    def test_displayname_without_prefix(self):
        testperiodtag = mommy.make('core.PeriodTag', tag='a')
        self.assertEquals('a', testperiodtag.displayname)

    def test_displayname_with_prefix(self):
        testperiodtag = mommy.make('core.PeriodTag', prefix='a', tag='b')
        self.assertEquals('a:b', testperiodtag.displayname)

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

    def test_filter_editable_tags(self):
        mommy.make('core.PeriodTag')
        mommy.make('core.PeriodTag')
        mommy.make('core.PeriodTag', prefix='a')
        mommy.make('core.PeriodTag', prefix='b')
        self.assertEquals(2, PeriodTag.objects.filter_editable_tags().count())

    def test_filter_editable_tags_on_period(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod)
        mommy.make('core.PeriodTag', period=testperiod, prefix='a')
        mommy.make('core.PeriodTag', period=testperiod, prefix='b')
        self.assertEquals(2, PeriodTag.objects.filter_editable_tags_on_period(period=testperiod).count())

    def test_filter_tags_string_list_on_period(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, prefix='prefix', tag='a')
        mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mommy.make('core.PeriodTag', period=testperiod, tag='b')
        self.assertListEqual(['a', 'b', 'prefix:a'],
                             PeriodTag.objects.tags_string_list_on_period(period=testperiod))

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

    def test_filter_tags_on_period(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod, tag='a')
        mommy.make('core.PeriodTag', period=testperiod, tag='b')
        mommy.make('core.PeriodTag', period=testperiod, tag='c')
        self.assertEquals(3, PeriodTag.objects.filter(period=testperiod).count())

    def test_filter_distinct_tags(self):
        testperiod1 = mommy.make('core.Period')
        testperiod2 = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod1, tag='a')
        mommy.make('core.PeriodTag', period=testperiod1, tag='b')
        mommy.make('core.PeriodTag', period=testperiod2, tag='a')
        mommy.make('core.PeriodTag', period=testperiod2, tag='b')
        distinct_tags = PeriodTag.objects.filter_distinct_tags()
        self.assertEquals(2, distinct_tags.count())
        self.assertEquals('a', distinct_tags[0].tag)
        self.assertEquals('b', distinct_tags[1].tag)

    def get_tags_for_related_student_user(self):
        testperiod1 = mommy.make('core.Period')
        testperiod2 = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.PeriodTag', period=testperiod1, tag='period1_tag1')\
            .relatedstudents.add(mommy.make('core.RelatedStudent', user=testuser))
        mommy.make('core.PeriodTag', period=testperiod2, tag='period2_tag1')\
            .relatedstudents.add(mommy.make('core.RelatedStudent', user=testuser))
        mommy.make('core.PeriodTag', period=testperiod2, tag='period2_tag2')

        student_tags = PeriodTag.objects.filter_tags_for_related_student_user(user=testuser)
        self.assertEquals(2, student_tags.count())
        student_tags_string_list = student_tags.values_list('tag', flat=True)
        self.assertIn('period1_tag1', student_tags_string_list)
        self.assertIn('period2_tag1', student_tags_string_list)
        self.assertNotIn('period2_tag2', student_tags_string_list)

    def get_tags_for_related_student_user_on_period(self):
        testperiod1 = mommy.make('core.Period')
        testperiod2 = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.PeriodTag', period=testperiod1, tag='period1_tag')\
            .relatedstudents.add(mommy.make('core.RelatedStudent', user=testuser))
        mommy.make('core.PeriodTag', period=testperiod2, tag='period2_tag') \
            .relatedstudents.add(mommy.make('core.RelatedStudent', user=testuser))
        period_tags = PeriodTag.objects\
            .filter_tags_for_related_student_user_on_period(user=testuser, period=testperiod1)
        self.assertEquals(1, period_tags.count())
        self.assertEquals('period1_tag', period_tags[0].tag)

    def get_tags_for_related_examiner_user(self):
        testperiod1 = mommy.make('core.Period')
        testperiod2 = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.PeriodTag', period=testperiod1, tag='period1_tag1')\
            .relatedexaminer.add(mommy.make('core.RelatedExaminer', user=testuser))
        mommy.make('core.PeriodTag', period=testperiod2, tag='period2_tag1')\
            .relatedexaminers(mommy.make('core.RelatedExaminer', user=testuser))
        mommy.make('core.PeriodTag', period=testperiod2, tag='period2_tag2')

        examiner_tags = PeriodTag.objects.filter_tags_for_related_examiner_user(user=testuser)
        self.assertEquals(2, examiner_tags.count())
        examiner_tags_string_list = examiner_tags.values_list('tag', flat=True)
        self.assertIn('period1_tag1', examiner_tags_string_list)
        self.assertIn('period2_tag1', examiner_tags_string_list)
        self.assertNotIn('period2_tag2', examiner_tags_string_list)

    def get_tags_for_related_examiner_user_on_period(self):
        testperiod1 = mommy.make('core.Period')
        testperiod2 = mommy.make('core.Period')
        testuser = mommy.make(settings.AUTH_USER_MODEL)
        mommy.make('core.PeriodTag', period=testperiod1, tag='period1_tag')\
            .relatedexaminers.add(mommy.make('core.RelatedExaminer', user=testuser))
        mommy.make('core.PeriodTag', period=testperiod2, tag='period2_tag') \
            .relatedexaminers.add(mommy.make('core.RelatedExaminer', user=testuser))
        period_tags = PeriodTag.objects\
            .filter_tags_for_related_examiner_user_on_period(user=testuser, period=testperiod1)
        self.assertEquals(1, period_tags.count())
        self.assertEquals('period1_tag', period_tags[0].tag)

    def get_all_tags_for_active_periods(self):
        testperiod1 = mommy.make_recipe('devilry.apps.core.period_active')
        testperiod2 = mommy.make_recipe('devilry.apps.core.period_old')
        mommy.make('core.PeriodTag', period=testperiod1, tag='tag_active')
        mommy.make('core.PeriodTag', period=testperiod2, tag='tag_old')
        active_periodtags = PeriodTag.objects.get_all_tags_for_active_periods()
        self.assertEquals(1, active_periodtags.count())
        self.assertEquals('tag_active', active_periodtags[0].tag)

    def test_annotate_with_relatedexaminers_count(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod)
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod)
        testperiodtag2.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod)
        )
        testperiodtag2.relatedexaminers.add(
            mommy.make('core.RelatedExaminer', period=testperiod)
        )
        queryset = PeriodTag.objects.annotate_with_relatedexaminers_count()
        queryset_without_relatedexaminers = queryset.filter(annotated_relatedexaminers_count__lt=2)
        queryset_with_relatedexaminers = queryset.filter(annotated_relatedexaminers_count__gte=2)
        self.assertEquals(queryset_without_relatedexaminers[0].annotated_relatedexaminers_count, 0)
        self.assertEquals(queryset_with_relatedexaminers[0].annotated_relatedexaminers_count, 2)

    def test_annotate_with_relatedstudents_count(self):
        testperiod = mommy.make('core.Period')
        mommy.make('core.PeriodTag', period=testperiod)
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod)
        testperiodtag2.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=testperiod)
        )
        testperiodtag2.relatedstudents.add(
            mommy.make('core.RelatedStudent', period=testperiod)
        )
        queryset = PeriodTag.objects.annotate_with_relatedstudents_count()
        queryset_without_relatedstudents = queryset.filter(annotated_relatedstudents_count__lt=2)
        queryset_with_relatedstudents = queryset.filter(annotated_relatedstudents_count__gte=2)
        self.assertEquals(queryset_without_relatedstudents[0].annotated_relatedstudents_count, 0)
        self.assertEquals(queryset_with_relatedstudents[0].annotated_relatedstudents_count, 2)
