import htmls
import mock
from django import test
from model_mommy import mommy

from devilry.devilry_admin.cradminextensions.multiselect2 import multiselect2_relatedstudent


class TestSelectedItem(test.TestCase):
    def test_title_without_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(multiselect2_relatedstudent.SelectedItem(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(multiselect2_relatedstudent.SelectedItem(value=relatedstudent).render())
        self.assertEqual(
            'Test User',
            selector.one('.django-cradmin-multiselect2-target-selected-item-title').alltext_normalized)

    def test_description_without_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(multiselect2_relatedstudent.SelectedItem(value=relatedstudent).render())
        self.assertFalse(
            selector.exists('.django-cradmin-multiselect2-target-selected-item-description'))

    def test_description_with_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(multiselect2_relatedstudent.SelectedItem(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-multiselect2-target-selected-item-description').alltext_normalized)


class TestItemValue(test.TestCase):
    def test_title_without_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(multiselect2_relatedstudent.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-multiselect2-itemvalue-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(multiselect2_relatedstudent.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'Test User',
            selector.one('.django-cradmin-multiselect2-itemvalue-title').alltext_normalized)

    def test_description_without_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(multiselect2_relatedstudent.ItemValue(value=relatedstudent).render())
        self.assertFalse(
            selector.exists('.django-cradmin-multiselect2-itemvalue-description'))

    def test_description_with_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(multiselect2_relatedstudent.ItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-multiselect2-itemvalue-description').alltext_normalized)


class TestTarget(test.TestCase):
    def test_with_items_title(self):
        selector = htmls.S(multiselect2_relatedstudent.Target().render(request=mock.MagicMock()))
        self.assertEqual(
            'Selected students',
            selector.one('.django-cradmin-multiselect2-target-title').alltext_normalized)

    def test_without_items_text(self):
        selector = htmls.S(multiselect2_relatedstudent.Target().render(request=mock.MagicMock()))
        self.assertEqual(
            'No students selected',
            selector.one('.django-cradmin-multiselect2-target-without-items-content').alltext_normalized)
