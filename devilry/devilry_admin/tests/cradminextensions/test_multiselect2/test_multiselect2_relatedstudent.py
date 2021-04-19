import htmls
import mock
from django import test
from django import forms
from model_bakery import baker

from devilry.apps.core.models import RelatedStudent
from devilry.devilry_admin.cradminextensions.multiselect2 import multiselect2_relatedstudent


class TestSelectedItem(test.TestCase):
    def test_title_without_fullname(self):
        relatedstudent = baker.make('core.RelatedStudent',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(multiselect2_relatedstudent.SelectedItem(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.cradmin-legacy-multiselect2-target-selected-item-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedstudent = baker.make('core.RelatedStudent',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(multiselect2_relatedstudent.SelectedItem(value=relatedstudent).render())
        self.assertEqual(
            'Test User(test@example.com)',
            selector.one('.cradmin-legacy-multiselect2-target-selected-item-title').alltext_normalized)

    def test_description_without_tags(self):
        relatedstudent = baker.make('core.RelatedStudent')
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(multiselect2_relatedstudent.SelectedItem(value=relatedstudent).render())
        self.assertFalse(
            selector.exists('.cradmin-legacy-multiselect2-target-selected-item-description'))

    # def test_description_with_tags(self):
    #     relatedstudent = baker.make('core.RelatedStudent')
    #     baker.make('core.RelatedStudentTag', tag='a', relatedstudent=relatedstudent)
    #     baker.make('core.RelatedStudentTag', tag='b', relatedstudent=relatedstudent)
    #     relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
    #     selector = htmls.S(multiselect2_relatedstudent.SelectedItem(value=relatedstudent).render())
    #     self.assertEqual(
    #         'a, b',
    #         selector.one('.cradmin-legacy-multiselect2-target-selected-item-description').alltext_normalized)

    def test_description_with_tags(self):
        testperiod = baker.make('core.Period')
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod, tag='b')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod)
        testperiodtag1.relatedstudents.add(relatedstudent)
        testperiodtag2.relatedstudents.add(relatedstudent)
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(multiselect2_relatedstudent.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'a, b',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestItemValue(test.TestCase):
    def test_title_without_fullname(self):
        relatedstudent = baker.make('core.RelatedStudent',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(multiselect2_relatedstudent.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedstudent = baker.make('core.RelatedStudent',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(multiselect2_relatedstudent.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'Test User(test@example.com)',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_without_tags(self):
        relatedstudent = baker.make('core.RelatedStudent')
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(multiselect2_relatedstudent.ItemValue(value=relatedstudent).render())
        self.assertFalse(
            selector.exists('.cradmin-legacy-listbuilder-itemvalue-titledescription-description'))

    def test_description_with_tags(self):
        testperiod = baker.make('core.Period')
        testperiodtag1 = baker.make('core.PeriodTag', period=testperiod, tag='a')
        testperiodtag2 = baker.make('core.PeriodTag', period=testperiod, tag='b')
        relatedstudent = baker.make('core.RelatedStudent', period=testperiod)
        testperiodtag1.relatedstudents.add(relatedstudent)
        testperiodtag2.relatedstudents.add(relatedstudent)
        relatedstudent = RelatedStudent.objects.prefetch_syncsystemtag_objects().get(id=relatedstudent.id)
        selector = htmls.S(multiselect2_relatedstudent.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'a, b',
            selector.one('.cradmin-legacy-listbuilder-itemvalue-titledescription-description').alltext_normalized)


class TestTarget(test.TestCase):
    def test_with_items_title(self):
        selector = htmls.S(multiselect2_relatedstudent.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual(
            'Selected students',
            selector.one('.cradmin-legacy-multiselect2-target-title').alltext_normalized)

    def test_without_items_text(self):
        selector = htmls.S(multiselect2_relatedstudent.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual(
            'No students selected',
            selector.one('.cradmin-legacy-multiselect2-target-without-items-content').alltext_normalized)
