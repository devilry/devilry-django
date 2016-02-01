import htmls
from django import test
from model_mommy import mommy

from devilry.devilry_admin.cradminextensions.listbuilder import listbuilder_relatedstudent


class TestOnPeriodItemValue(test.TestCase):
    def test_title_without_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(listbuilder_relatedstudent.OnPeriodItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_title_with_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(listbuilder_relatedstudent.OnPeriodItemValue(value=relatedstudent).render())
        self.assertEqual(
            'Test User',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-title').alltext_normalized)

    def test_description_without_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__shortname='test@example.com',
                                    user__fullname='')
        selector = htmls.S(listbuilder_relatedstudent.OnPeriodItemValue(value=relatedstudent).render())
        self.assertFalse(
            selector.exists('.django-cradmin-listbuilder-itemvalue-titledescription-description'))

    def test_description_with_fullname(self):
        relatedstudent = mommy.make('core.RelatedStudent',
                                    user__fullname='Test User',
                                    user__shortname='test@example.com')
        selector = htmls.S(listbuilder_relatedstudent.OnPeriodItemValue(value=relatedstudent).render())
        self.assertEqual(
            'test@example.com',
            selector.one('.django-cradmin-listbuilder-itemvalue-titledescription-description').alltext_normalized)
