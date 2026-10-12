from django import test
from django_cradmin import uicontainer


class TestEscapedText(test.TestCase):
    def test_no_text(self):
        container = uicontainer.text.EscapedText(text="").bootstrap()
        output = container.render()
        self.assertEqual(output, "\n")

    def test_simple_text(self):
        container = uicontainer.text.EscapedText(text="test").bootstrap()
        output = container.render()
        self.assertEqual(output, "test\n")

    def test_html_text(self):
        container = uicontainer.text.EscapedText(text="<p>Hello</p>").bootstrap()
        output = container.render()
        self.assertEqual(output, "&lt;p&gt;Hello&lt;/p&gt;\n")


class TestHtml(test.TestCase):
    def test_no_html(self):
        container = uicontainer.text.Html(html="").bootstrap()
        output = container.render()
        self.assertEqual(output.strip(), "")

    def test_html(self):
        container = uicontainer.text.Html(html="<p>Hello</p>").bootstrap()
        output = container.render()
        self.assertEqual(output.strip(), "<p>Hello</p>")

    def test_get_default_html(self):
        class CustomHtml(uicontainer.text.Html):
            def get_default_html(self):
                return "test"

        container = CustomHtml().bootstrap()
        output = container.render()
        self.assertEqual(output.strip(), "test")

    def test_get_default_html_overridden_by_kwarg(self):
        class CustomHtml(uicontainer.text.Html):
            def get_default_html(self):
                return "test"

        container = CustomHtml(html="overridden").bootstrap()
        output = container.render()
        self.assertEqual(output.strip(), "overridden")
