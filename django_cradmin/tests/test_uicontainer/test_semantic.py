import htmls
from django import test
from django_cradmin import uicontainer


class TestParagraph(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Paragraph().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("p"))

    def test_no_text(self):
        container = uicontainer.semantic.Paragraph().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("p").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.semantic.Paragraph(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("p").alltext_normalized, "test")


class TestLink(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Link().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("a"))

    def test_no_text(self):
        container = uicontainer.semantic.Link().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("a").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.semantic.Link(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("a").alltext_normalized, "test")

    def test_no_href(self):
        container = uicontainer.semantic.Link().bootstrap()
        selector = htmls.S(container.render())
        self.assertFalse(selector.one("a").hasattribute("href"))

    def test_with_href(self):
        container = uicontainer.semantic.Link(href="http://example.com").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("a")["href"], "http://example.com")

    def test_no_target(self):
        container = uicontainer.semantic.Link().bootstrap()
        selector = htmls.S(container.render())
        self.assertFalse(selector.one("a").hasattribute("target"))

    def test_with_target(self):
        container = uicontainer.semantic.Link(target="_blank").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("a")["target"], "_blank")


class TestStrong(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Strong().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("strong"))

    def test_no_text(self):
        container = uicontainer.semantic.Strong().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("strong").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.semantic.Strong(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("strong").alltext_normalized, "test")


class TestEm(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Em().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("em"))

    def test_no_text(self):
        container = uicontainer.semantic.Em().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("em").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.semantic.Em(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("em").alltext_normalized, "test")


class TestH1(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.H1().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("h1"))

    def test_no_text(self):
        container = uicontainer.semantic.H1().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h1").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.semantic.H1(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h1").alltext_normalized, "test")


class TestH2(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.H2().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("h2"))

    def test_no_text(self):
        container = uicontainer.semantic.H2().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h2").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.semantic.H2(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h2").alltext_normalized, "test")


class TestH3(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.H3().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("h3"))

    def test_no_text(self):
        container = uicontainer.semantic.H3().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h3").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.semantic.H3(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h3").alltext_normalized, "test")


class TestH4(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.H4().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("h4"))

    def test_no_text(self):
        container = uicontainer.semantic.H4().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h4").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.semantic.H4(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h4").alltext_normalized, "test")


class TestSection(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Section().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("section"))


class TestHeader(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Header().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("header"))


class TestFooter(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Footer().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("footer"))


class TestMain(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Main().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("main"))

    def test_role(self):
        container = uicontainer.semantic.Main().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("main")["role"], "main")


class TestNav(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Nav().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("nav"))


class TestUl(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Ul().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("ul"))


class TestOl(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Ol().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("ol"))


class TestLi(test.TestCase):
    def test_sanity(self):
        container = uicontainer.semantic.Li().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("li"))

    def test_no_text(self):
        container = uicontainer.semantic.Li().bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("li").alltext_normalized, "")

    def test_with_text(self):
        container = uicontainer.semantic.Li(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("li").alltext_normalized, "test")
