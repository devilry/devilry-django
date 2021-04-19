

from django import test
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings

from model_bakery import baker

from devilry.apps.core.models.period_tag import PeriodTag
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestPeriodTag(test.TestCase):
    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_full_clean_tag_cannot_be_blank(self):
        with self.assertRaises(ValidationError):
            baker.make('core.PeriodTag', tag='').full_clean()

    def test_displayname_without_prefix(self):
        testperiodtag = baker.make('core.PeriodTag', tag='a')
        self.assertEqual('a', testperiodtag.displayname)

    def test_displayname_with_prefix(self):
        testperiodtag = baker.make('core.PeriodTag', prefix='a', tag='b')
        self.assertEqual('a:b', testperiodtag.displayname)

    def test_unique_together_without_prefix(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='a')
        with self.assertRaises(IntegrityError):
            baker.make('core.PeriodTag', period=testperiod, tag='a')

    def test_unique_together_with_prefix(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, prefix='a', tag='b')
        with self.assertRaises(IntegrityError):
            baker.make('core.PeriodTag', period=testperiod, prefix='a', tag='b')

    def test_filter_editable_tags(self):
        baker.make('core.PeriodTag')
        baker.make('core.PeriodTag')
        baker.make('core.PeriodTag', prefix='a')
        baker.make('core.PeriodTag', prefix='b')
        self.assertEqual(2, PeriodTag.objects.filter_editable_tags().count())

    def test_filter_editable_tags_on_period(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod)
        baker.make('core.PeriodTag', period=testperiod)
        baker.make('core.PeriodTag', period=testperiod, prefix='a')
        baker.make('core.PeriodTag', period=testperiod, prefix='b')
        self.assertEqual(2, PeriodTag.objects.filter_editable_tags_on_period(period=testperiod).count())

    def test_filter_tags_string_list_on_period(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, prefix='prefix', tag='a')
        baker.make('core.PeriodTag', period=testperiod, tag='a')
        baker.make('core.PeriodTag', period=testperiod, tag='b')
        self.assertListEqual(['a', 'b', 'prefix:a'],
                             PeriodTag.objects.tags_string_list_on_period(period=testperiod))

    def test_auto_created_datetime(self):
        testperiodtag = baker.make('core.PeriodTag')
        self.assertIsNotNone(testperiodtag.created_datetime)

    def test_add_relatedstudents(self):
        testperiodtag = baker.make('core.PeriodTag')
        relatedstudent1 = baker.make('core.RelatedStudent')
        relatedstudent2 = baker.make('core.RelatedStudent')
        relatedstudent3 = baker.make('core.RelatedStudent')
        testperiodtag.relatedstudents.add(relatedstudent1)
        testperiodtag.relatedstudents.add(relatedstudent2)
        testperiodtag.relatedstudents.add(relatedstudent3)
        self.assertEqual(3, PeriodTag.objects.get(id=testperiodtag.id).relatedstudents.count())

    def test_add_relatedexaminers(self):
        testperiodtag = baker.make('core.PeriodTag')
        relatedexaminer1 = baker.make('core.RelatedExaminer')
        relatedexaminer2 = baker.make('core.RelatedExaminer')
        relatedexaminer3 = baker.make('core.RelatedExaminer')
        testperiodtag.relatedexaminers.add(relatedexaminer1)
        testperiodtag.relatedexaminers.add(relatedexaminer2)
        testperiodtag.relatedexaminers.add(relatedexaminer3)
        self.assertEqual(3, PeriodTag.objects.get(id=testperiodtag.id).relatedexaminers.count())

    def test_add_relatedstudents_and_examiners(self):
        testperiodtag = baker.make('core.PeriodTag')
        relatedexaminer1 = baker.make('core.RelatedExaminer')
        relatedexaminer2 = baker.make('core.RelatedExaminer')
        relatedexaminer3 = baker.make('core.RelatedExaminer')
        testperiodtag.relatedexaminers.add(relatedexaminer1)
        testperiodtag.relatedexaminers.add(relatedexaminer2)
        testperiodtag.relatedexaminers.add(relatedexaminer3)
        relatedstudent1 = baker.make('core.RelatedStudent')
        relatedstudent2 = baker.make('core.RelatedStudent')
        relatedstudent3 = baker.make('core.RelatedStudent')
        testperiodtag.relatedstudents.add(relatedstudent1)
        testperiodtag.relatedstudents.add(relatedstudent2)
        testperiodtag.relatedstudents.add(relatedstudent3)
        self.assertEqual(3, PeriodTag.objects.get(id=testperiodtag.id).relatedstudents.count())
        self.assertEqual(3, PeriodTag.objects.get(id=testperiodtag.id).relatedexaminers.count())

    def test_filter_tags_on_period(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod, tag='a')
        baker.make('core.PeriodTag', period=testperiod, tag='b')
        baker.make('core.PeriodTag', period=testperiod, tag='c')
        self.assertEqual(3, PeriodTag.objects.filter(period=testperiod).count())

    def test_filter_distinct_tags(self):
        testperiod1 = baker.make('core.Period')
        testperiod2 = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod1, tag='a')
        baker.make('core.PeriodTag', period=testperiod1, tag='b')
        baker.make('core.PeriodTag', period=testperiod2, tag='a')
        baker.make('core.PeriodTag', period=testperiod2, tag='b')
        distinct_tags = PeriodTag.objects.filter_distinct_tags()
        self.assertEqual(2, distinct_tags.count())
        self.assertEqual('a', distinct_tags[0].tag)
        self.assertEqual('b', distinct_tags[1].tag)

    def get_tags_for_related_student_user(self):
        testperiod1 = baker.make('core.Period')
        testperiod2 = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.PeriodTag', period=testperiod1, tag='period1_tag1')\
            .relatedstudents.add(baker.make('core.RelatedStudent', user=testuser))
        baker.make('core.PeriodTag', period=testperiod2, tag='period2_tag1')\
            .relatedstudents.add(baker.make('core.RelatedStudent', user=testuser))
        baker.make('core.PeriodTag', period=testperiod2, tag='period2_tag2')

        student_tags = PeriodTag.objects.filter_tags_for_related_student_user(user=testuser)
        self.assertEqual(2, student_tags.count())
        student_tags_string_list = student_tags.values_list('tag', flat=True)
        self.assertIn('period1_tag1', student_tags_string_list)
        self.assertIn('period2_tag1', student_tags_string_list)
        self.assertNotIn('period2_tag2', student_tags_string_list)

    def get_tags_for_related_student_user_on_period(self):
        testperiod1 = baker.make('core.Period')
        testperiod2 = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.PeriodTag', period=testperiod1, tag='period1_tag')\
            .relatedstudents.add(baker.make('core.RelatedStudent', user=testuser))
        baker.make('core.PeriodTag', period=testperiod2, tag='period2_tag') \
            .relatedstudents.add(baker.make('core.RelatedStudent', user=testuser))
        period_tags = PeriodTag.objects\
            .filter_tags_for_related_student_user_on_period(user=testuser, period=testperiod1)
        self.assertEqual(1, period_tags.count())
        self.assertEqual('period1_tag', period_tags[0].tag)

    def get_tags_for_related_examiner_user(self):
        testperiod1 = baker.make('core.Period')
        testperiod2 = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.PeriodTag', period=testperiod1, tag='period1_tag1')\
            .relatedexaminer.add(baker.make('core.RelatedExaminer', user=testuser))
        baker.make('core.PeriodTag', period=testperiod2, tag='period2_tag1')\
            .relatedexaminers(baker.make('core.RelatedExaminer', user=testuser))
        baker.make('core.PeriodTag', period=testperiod2, tag='period2_tag2')

        examiner_tags = PeriodTag.objects.filter_tags_for_related_examiner_user(user=testuser)
        self.assertEqual(2, examiner_tags.count())
        examiner_tags_string_list = examiner_tags.values_list('tag', flat=True)
        self.assertIn('period1_tag1', examiner_tags_string_list)
        self.assertIn('period2_tag1', examiner_tags_string_list)
        self.assertNotIn('period2_tag2', examiner_tags_string_list)

    def get_tags_for_related_examiner_user_on_period(self):
        testperiod1 = baker.make('core.Period')
        testperiod2 = baker.make('core.Period')
        testuser = baker.make(settings.AUTH_USER_MODEL)
        baker.make('core.PeriodTag', period=testperiod1, tag='period1_tag')\
            .relatedexaminers.add(baker.make('core.RelatedExaminer', user=testuser))
        baker.make('core.PeriodTag', period=testperiod2, tag='period2_tag') \
            .relatedexaminers.add(baker.make('core.RelatedExaminer', user=testuser))
        period_tags = PeriodTag.objects\
            .filter_tags_for_related_examiner_user_on_period(user=testuser, period=testperiod1)
        self.assertEqual(1, period_tags.count())
        self.assertEqual('period1_tag', period_tags[0].tag)

    def get_all_tags_for_active_periods(self):
        testperiod1 = baker.make_recipe('devilry.apps.core.period_active')
        testperiod2 = baker.make_recipe('devilry.apps.core.period_old')
        baker.make('core.PeriodTag', period=testperiod1, tag='tag_active')
        baker.make('core.PeriodTag', period=testperiod2, tag='tag_old')
        active_periodtags = PeriodTag.objects.get_all_tags_for_active_periods()
        self.assertEqual(1, active_periodtags.count())
        self.assertEqual('tag_active', active_periodtags[0].tag)

    def test_annotate_with_relatedexaminers_count(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod)
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod)
        testperiodtag2.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod)
        )
        testperiodtag2.relatedexaminers.add(
            baker.make('core.RelatedExaminer', period=testperiod)
        )
        queryset = PeriodTag.objects.annotate_with_relatedexaminers_count()
        queryset_without_relatedexaminers = queryset.filter(annotated_relatedexaminers_count__lt=2)
        queryset_with_relatedexaminers = queryset.filter(annotated_relatedexaminers_count__gte=2)
        self.assertEqual(queryset_without_relatedexaminers[0].annotated_relatedexaminers_count, 0)
        self.assertEqual(queryset_with_relatedexaminers[0].annotated_relatedexaminers_count, 2)

    def test_annotate_with_relatedstudents_count(self):
        testperiod = baker.make('core.Period')
        baker.make('core.PeriodTag', period=testperiod)
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod)
        testperiodtag2.relatedstudents.add(
            baker.make('core.RelatedStudent', period=testperiod)
        )
        testperiodtag2.relatedstudents.add(
            baker.make('core.RelatedStudent', period=testperiod)
        )
        queryset = PeriodTag.objects.annotate_with_relatedstudents_count()
        queryset_without_relatedstudents = queryset.filter(annotated_relatedstudents_count__lt=2)
        queryset_with_relatedstudents = queryset.filter(annotated_relatedstudents_count__gte=2)
        self.assertEqual(queryset_without_relatedstudents[0].annotated_relatedstudents_count, 0)
        self.assertEqual(queryset_with_relatedstudents[0].annotated_relatedstudents_count, 2)
