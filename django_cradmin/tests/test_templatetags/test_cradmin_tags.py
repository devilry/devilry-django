from django import test

from django_cradmin.templatetags import cradmin_tags


class TestCradminTestCssClass(test.TestCase):
    def test_test_css_classes_disabled(self):
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            self.assertEqual("", cradmin_tags.cradmin_test_css_class("my-css-class"))

    def test_test_css_classes_enabled(self):
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=True):
            self.assertEqual("  test-my-css-class  ", cradmin_tags.cradmin_test_css_class("my-css-class"))
