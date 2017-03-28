import htmls
from django import test
from model_mommy import mommy

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedstudent


class TestOnPeriodItemValue(test.TestCase):
    def test_title_without_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(listbuilder_relatedstudent.ReadOnlyItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(listbuilder_relatedstudent.ReadOnlyItemValue(value=relatedstudent).render())
        self.assertEqual(
            'Test User(test@example.com)',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_without_tags(self):
        relatedstudent = mommy.make('core.RelatedStudent')
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(listbuilder_relatedstudent.ReadOnlyItemValue(value=relatedstudent).render())
        self.assertFalse(
            selector.exists('.django-cradmin-listbuilder-itemvalue-titledescription-description'))

    # def test_description_with_tags(self):
    #     relatedstudent = mommy.make('core.RelatedStudent')
    #     mommy.make('core.RelatedStudentTag', tag='a', relatedstudent=relatedstudent)
    #     mommy.make('core.RelatedStudentTag', tag='b', relatedstudent=relatedstudent)
    #     relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
    #     selector = htmls.S(listbuilder_relatedstudent.ReadOnlyItemValue(value=relatedstudent).render())
    #     self.assertEqual(
    #         'a, b',
    #         selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)

    def test_description_with_tags(self):
        testperiod = mommy.make('core.Period')
        testperiodtag1 = mommy.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag2 = mommy.make('core.PeriodTag', period=testperiod, tag='b')
        relatedstudent = mommy.make('core.RelatedStudent', period=testperiod)
        testperiodtag1.relatedstudents.add(relatedstudent)
        testperiodtag2.relatedstudents.add(relatedstudent)
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(listbuilder_relatedstudent.ReadOnlyItemValue(value=relatedstudent).render())
        self.assertEqual(
            'a, b',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)
