# -*- coding: utf-8 -*-


from django import test
from cradmin_legacy import cradmin_testhelpers
from model_bakery import baker

from devilry.apps.core.models import PeriodTag
from devilry.apps.core.models import RelatedExaminer, RelatedStudent
from devilry.devilry_admin.views.period.manage_tags import manage_tags
from devilry.devilry_dbcache.customsql import AssignmentGroupDbCacheCustomSql


class TestAddRelatedExaminersToTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.RelatedExaminerAddView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_add_single_relatedexaminer_to_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedexaminer = baker.make('core.RelatedExaminer', period=testperiod)
        self.assertEqual(testrelatedexaminer.periodtag_set.count(), 0)
        self.assertEqual(testperiodtag.relatedexaminers.count(), 0)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedexaminer.id]
                }
            }
        )
        relatedexaminer = RelatedExaminer.objects.get(id=testrelatedexaminer.id)
        relatedexaminer_tag_ids = relatedexaminer.periodtag_set.all().values_list('id', flat=True)
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        periodtag_relatedexaminers_ids = periodtag.relatedexaminers.all().values_list('id', flat=True)
        self.assertEqual(relatedexaminer.periodtag_set.count(), 1)
        self.assertEqual(periodtag.relatedexaminers.count(), 1)
        self.assertIn(relatedexaminer.id, periodtag_relatedexaminers_ids)
        self.assertIn(periodtag.id, relatedexaminer_tag_ids)

    def test_add_multiple_relatedexaminer_to_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedexaminer1 = baker.make('core.RelatedExaminer', period=testperiod)
        testrelatedexaminer2 = baker.make('core.RelatedExaminer', period=testperiod)
        testrelatedexaminer3 = baker.make('core.RelatedExaminer', period=testperiod)
        self.assertEqual(testrelatedexaminer1.periodtag_set.count(), 0)
        self.assertEqual(testrelatedexaminer2.periodtag_set.count(), 0)
        self.assertEqual(testrelatedexaminer3.periodtag_set.count(), 0)
        self.assertEqual(testperiodtag.relatedexaminers.count(), 0)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedexaminer1.id, testrelatedexaminer2.id, testrelatedexaminer3.id]
                }
            }
        )
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        periodtag_relatedexaminers_ids = periodtag.relatedexaminers.all().values_list('id', flat=True)
        self.assertEqual(len(periodtag_relatedexaminers_ids), 3)
        self.assertIn(testrelatedexaminer1.id, periodtag_relatedexaminers_ids)
        self.assertIn(testrelatedexaminer2.id, periodtag_relatedexaminers_ids)
        self.assertIn(testrelatedexaminer3.id, periodtag_relatedexaminers_ids)

    def test_add_only_selected_relatedexaminers_are_added(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedexaminer1 = baker.make('core.RelatedExaminer', period=testperiod)
        testrelatedexaminer2 = baker.make('core.RelatedExaminer', period=testperiod)
        testrelatedexaminer3 = baker.make('core.RelatedExaminer', period=testperiod)
        self.assertEqual(testrelatedexaminer1.periodtag_set.count(), 0)
        self.assertEqual(testrelatedexaminer2.periodtag_set.count(), 0)
        self.assertEqual(testrelatedexaminer3.periodtag_set.count(), 0)
        self.assertEqual(testperiodtag.relatedexaminers.count(), 0)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedexaminer1.id, testrelatedexaminer2.id]
                }
            }
        )
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        periodtag_relatedexaminers_ids = periodtag.relatedexaminers.all().values_list('id', flat=True)
        self.assertIn(testrelatedexaminer1.id, periodtag_relatedexaminers_ids)
        self.assertIn(testrelatedexaminer2.id, periodtag_relatedexaminers_ids)
        self.assertNotIn(testrelatedexaminer3.id, periodtag_relatedexaminers_ids)


class TestRemoveRelatedExaminersFromTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.RelatedExaminerRemoveView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_remove_single_relatedexaminer_from_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedexaminer = baker.make('core.RelatedExaminer', period=testperiod)
        testperiodtag.relatedexaminers.add(testrelatedexaminer)
        self.assertEqual(testrelatedexaminer.periodtag_set.count(), 1)
        self.assertEqual(testperiodtag.relatedexaminers.count(), 1)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedexaminer.id]
                }
            }
        )
        relatedexaminer = RelatedExaminer.objects.get(id=testrelatedexaminer.id)
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        self.assertEqual(relatedexaminer.periodtag_set.count(), 0)
        self.assertEqual(periodtag.relatedexaminers.count(), 0)

    def test_remove_multiple_relatedexaminers_to_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedexaminer1 = baker.make('core.RelatedExaminer', period=testperiod)
        testrelatedexaminer2 = baker.make('core.RelatedExaminer', period=testperiod)
        testrelatedexaminer3 = baker.make('core.RelatedExaminer', period=testperiod)
        testperiodtag.relatedexaminers.add(testrelatedexaminer1)
        testperiodtag.relatedexaminers.add(testrelatedexaminer2)
        testperiodtag.relatedexaminers.add(testrelatedexaminer3)
        self.assertEqual(testrelatedexaminer1.periodtag_set.count(), 1)
        self.assertEqual(testrelatedexaminer2.periodtag_set.count(), 1)
        self.assertEqual(testrelatedexaminer3.periodtag_set.count(), 1)
        self.assertEqual(testperiodtag.relatedexaminers.count(), 3)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedexaminer1.id, testrelatedexaminer2.id, testrelatedexaminer3.id]
                }
            }
        )
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        relatedexaminer1 = RelatedExaminer.objects.get(id=testrelatedexaminer1.id)
        relatedexaminer2 = RelatedExaminer.objects.get(id=testrelatedexaminer2.id)
        relatedexaminer3 = RelatedExaminer.objects.get(id=testrelatedexaminer3.id)
        self.assertEqual(periodtag.relatedexaminers.count(), 0)
        self.assertEqual(relatedexaminer1.periodtag_set.count(), 0)
        self.assertEqual(relatedexaminer2.periodtag_set.count(), 0)
        self.assertEqual(relatedexaminer3.periodtag_set.count(), 0)

    def test_remove_only_selected_relatedexaminers_are_removed(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedexaminer1 = baker.make('core.RelatedExaminer', period=testperiod)
        testrelatedexaminer2 = baker.make('core.RelatedExaminer', period=testperiod)
        testrelatedexaminer3 = baker.make('core.RelatedExaminer', period=testperiod)
        testperiodtag.relatedexaminers.add(testrelatedexaminer1)
        testperiodtag.relatedexaminers.add(testrelatedexaminer2)
        testperiodtag.relatedexaminers.add(testrelatedexaminer3)
        self.assertEqual(testrelatedexaminer1.periodtag_set.count(), 1)
        self.assertEqual(testrelatedexaminer2.periodtag_set.count(), 1)
        self.assertEqual(testrelatedexaminer3.periodtag_set.count(), 1)
        self.assertEqual(testperiodtag.relatedexaminers.count(), 3)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedexaminer1.id, testrelatedexaminer2.id]
                }
            }
        )
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        periodtag_relatedexaminers_ids = periodtag.relatedexaminers.all().values_list('id', flat=True)
        self.assertNotIn(testrelatedexaminer1.id, periodtag_relatedexaminers_ids)
        self.assertNotIn(testrelatedexaminer2.id, periodtag_relatedexaminers_ids)
        self.assertIn(testrelatedexaminer3.id, periodtag_relatedexaminers_ids)


class TestAddRelatedStudentsToTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.RelatedStudentAddView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_add_single_relatedstudent_to_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedstudent = baker.make('core.RelatedStudent', period=testperiod)
        self.assertEqual(testrelatedstudent.periodtag_set.count(), 0)
        self.assertEqual(testperiodtag.relatedstudents.count(), 0)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedstudent.id]
                }
            }
        )
        relatedstudent = RelatedStudent.objects.get(id=testrelatedstudent.id)
        relatedstudent_tag_ids = relatedstudent.periodtag_set.all().values_list('id', flat=True)
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        periodtag_relatedstudents_ids = periodtag.relatedstudents.all().values_list('id', flat=True)
        self.assertEqual(relatedstudent.periodtag_set.count(), 1)
        self.assertEqual(periodtag.relatedstudents.count(), 1)
        self.assertIn(relatedstudent.id, periodtag_relatedstudents_ids)
        self.assertIn(periodtag.id, relatedstudent_tag_ids)

    def test_add_multiple_relatedstudents_to_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedstudent1 = baker.make('core.RelatedStudent', period=testperiod)
        testrelatedstudent2 = baker.make('core.RelatedStudent', period=testperiod)
        testrelatedstudent3 = baker.make('core.RelatedStudent', period=testperiod)
        self.assertEqual(testrelatedstudent1.periodtag_set.count(), 0)
        self.assertEqual(testrelatedstudent2.periodtag_set.count(), 0)
        self.assertEqual(testrelatedstudent3.periodtag_set.count(), 0)
        self.assertEqual(testperiodtag.relatedstudents.count(), 0)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedstudent1.id, testrelatedstudent2.id, testrelatedstudent3.id]
                }
            }
        )
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        periodtag_relatedstudents_ids = periodtag.relatedstudents.all().values_list('id', flat=True)
        self.assertEqual(len(periodtag_relatedstudents_ids), 3)
        self.assertIn(testrelatedstudent1.id, periodtag_relatedstudents_ids)
        self.assertIn(testrelatedstudent2.id, periodtag_relatedstudents_ids)
        self.assertIn(testrelatedstudent3.id, periodtag_relatedstudents_ids)

    def test_add_only_selected_relatedstudents_are_added(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedstudent1 = baker.make('core.RelatedStudent', period=testperiod)
        testrelatedstudent2 = baker.make('core.RelatedStudent', period=testperiod)
        testrelatedstudent3 = baker.make('core.RelatedStudent', period=testperiod)
        self.assertEqual(testrelatedstudent1.periodtag_set.count(), 0)
        self.assertEqual(testrelatedstudent2.periodtag_set.count(), 0)
        self.assertEqual(testrelatedstudent3.periodtag_set.count(), 0)
        self.assertEqual(testperiodtag.relatedstudents.count(), 0)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedstudent1.id, testrelatedstudent2.id]
                }
            }
        )
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        periodtag_relatedstudents_ids = periodtag.relatedstudents.all().values_list('id', flat=True)
        self.assertIn(testrelatedstudent1.id, periodtag_relatedstudents_ids)
        self.assertIn(testrelatedstudent2.id, periodtag_relatedstudents_ids)
        self.assertNotIn(testrelatedstudent3.id, periodtag_relatedstudents_ids)


class TestRemoveRelatedStudentsFromTag(test.TestCase, cradmin_testhelpers.TestCaseMixin):
    viewclass = manage_tags.RelatedStudentRemoveView

    def setUp(self):
        AssignmentGroupDbCacheCustomSql().initialize()

    def test_remove_single_relatedstudent_from_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedstudent = baker.make('core.RelatedStudent', period=testperiod)
        testperiodtag.relatedstudents.add(testrelatedstudent)
        self.assertEqual(testrelatedstudent.periodtag_set.count(), 1)
        self.assertEqual(testperiodtag.relatedstudents.count(), 1)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedstudent.id]
                }
            }
        )
        relatedstudent = RelatedStudent.objects.get(id=testrelatedstudent.id)
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        self.assertEqual(relatedstudent.periodtag_set.count(), 0)
        self.assertEqual(periodtag.relatedstudents.count(), 0)

    def test_remove_multiple_relatedstudents_from_tag(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedstudent1 = baker.make('core.RelatedStudent', period=testperiod)
        testrelatedstudent2 = baker.make('core.RelatedStudent', period=testperiod)
        testrelatedstudent3 = baker.make('core.RelatedStudent', period=testperiod)
        testperiodtag.relatedstudents.add(testrelatedstudent1)
        testperiodtag.relatedstudents.add(testrelatedstudent2)
        testperiodtag.relatedstudents.add(testrelatedstudent3)
        self.assertEqual(testrelatedstudent1.periodtag_set.count(), 1)
        self.assertEqual(testrelatedstudent2.periodtag_set.count(), 1)
        self.assertEqual(testrelatedstudent3.periodtag_set.count(), 1)
        self.assertEqual(testperiodtag.relatedstudents.count(), 3)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedstudent1.id, testrelatedstudent2.id, testrelatedstudent3.id]
                }
            }
        )
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        relatedstudent1 = RelatedStudent.objects.get(id=testrelatedstudent1.id)
        relatedstudent2 = RelatedStudent.objects.get(id=testrelatedstudent2.id)
        relatedstudent3 = RelatedStudent.objects.get(id=testrelatedstudent3.id)
        self.assertEqual(periodtag.relatedstudents.count(), 0)
        self.assertEqual(relatedstudent1.periodtag_set.count(), 0)
        self.assertEqual(relatedstudent2.periodtag_set.count(), 0)
        self.assertEqual(relatedstudent3.periodtag_set.count(), 0)

    def test_remove_only_selected_relatedexaminers_are_removed(self):
        testperiod = baker.make('core.Period')
        testperiodtag = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testrelatedstudent1 = baker.make('core.RelatedStudent', period=testperiod)
        testrelatedstudent2 = baker.make('core.RelatedStudent', period=testperiod)
        testrelatedstudent3 = baker.make('core.RelatedStudent', period=testperiod)
        testperiodtag.relatedstudents.add(testrelatedstudent1)
        testperiodtag.relatedstudents.add(testrelatedstudent2)
        testperiodtag.relatedstudents.add(testrelatedstudent3)
        self.assertEqual(testrelatedstudent1.periodtag_set.count(), 1)
        self.assertEqual(testrelatedstudent2.periodtag_set.count(), 1)
        self.assertEqual(testrelatedstudent3.periodtag_set.count(), 1)
        self.assertEqual(testperiodtag.relatedstudents.count(), 3)
        self.mock_http302_postrequest(
            cradmin_role=testperiod,
            viewkwargs={
                'tag_id': testperiodtag.id
            },
            requestkwargs={
                'data': {
                    'selected_items': [testrelatedstudent1.id, testrelatedstudent2.id]
                }
            }
        )
        periodtag = PeriodTag.objects.get(id=testperiodtag.id)
        periodtag_relatedstudents_ids = periodtag.relatedstudents.all().values_list('id', flat=True)
        self.assertNotIn(testrelatedstudent1.id, periodtag_relatedstudents_ids)
        self.assertNotIn(testrelatedstudent2.id, periodtag_relatedstudents_ids)
        self.assertIn(testrelatedstudent3.id, periodtag_relatedstudents_ids)
