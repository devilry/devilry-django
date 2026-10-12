import htmls
from django import test
from django_cradmin import uicontainer


class TestButton(test.TestCase):
    def test_sanity(self):
        container = uicontainer.button.Button().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("button"))

    def test_no_text(self):
        container = uicontainer.button.Button().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.button.Button(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button").alltext_normalized, "test")

    def test_button_type_default(self):
        container = uicontainer.button.Button().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["type"], "button")

    def test_button_type_kwarg(self):
        container = uicontainer.button.Button(button_type="submit").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["type"], "submit")

    def test_name_default(self):
        container = uicontainer.button.Button().bootstrap()
        selector = htmls.S(container.render())
        self.assertFalse(selector.one("button").hasattribute("name"))

    def test_name_kwarg(self):
        container = uicontainer.button.Button(name="testname").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["name"], "testname")

    def test_default_css_classes(self):
        container = uicontainer.button.Button().bootstrap()
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["class"], "button")


class TestButtonPrimary(test.TestCase):
    def test_button_type_default(self):
        container = uicontainer.button.ButtonPrimary().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["type"], "button")

    def test_default_css_classes(self):
        container = uicontainer.button.ButtonPrimary().bootstrap()
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["class"], "button  button--primary")


class TestButtonHistoryBack(test.TestCase):
    def test_button_type_default(self):
        container = uicontainer.button.ButtonHistoryBack().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["type"], "button")

    def test_default_css_classes(self):
        container = uicontainer.button.ButtonHistoryBack().bootstrap()
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["class"], "button")

    def test_onclick_attribute(self):
        container = uicontainer.button.ButtonHistoryBack().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["onclick"], "history.back();return false;")


class TestSubmit(test.TestCase):
    def test_sanity(self):
        container = uicontainer.button.Submit().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("button"))

    def test_no_text(self):
        container = uicontainer.button.Submit().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.button.Submit(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button").alltext_normalized, "test")

    def test_button_type_default(self):
        container = uicontainer.button.Submit().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["type"], "submit")

    def test_button_type_kwarg(self):
        container = uicontainer.button.Submit(button_type="button").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["type"], "button")

    def test_name_default(self):
        container = uicontainer.button.Submit().bootstrap()
        selector = htmls.S(container.render())
        self.assertFalse(selector.one("button").hasattribute("name"))

    def test_name_kwarg(self):
        container = uicontainer.button.Submit(name="testname").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["name"], "testname")

    def test_default_css_classes(self):
        container = uicontainer.button.Submit().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button").cssclasses_set, {"button", "test-submit"})


class TestSubmitPrimary(test.TestCase):
    def test_button_type_default(self):
        container = uicontainer.button.SubmitPrimary().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button")["type"], "submit")

    def test_default_css_classes(self):
        container = uicontainer.button.SubmitPrimary().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("button").cssclasses_set, {"button", "button--primary", "test-submit-primary"})
