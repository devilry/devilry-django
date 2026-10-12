import htmls
from django import test
from django_cradmin import uicontainer


class TestBlocklistItemTitle(test.TestCase):
    def test_sanity(self):
        container = uicontainer.blocklist.BlocklistItemTitle(html_tag="h1").bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("h1"))

    def test_default_css_classes(self):
        container = uicontainer.blocklist.BlocklistItemTitle(html_tag="h1").bootstrap()
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            selector = htmls.S(container.render())
        self.assertEqual(selector.one("h1")["class"], "blocklist__itemtitle")

    def test_no_text(self):
        container = uicontainer.blocklist.BlocklistItemTitle(html_tag="h1").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h1").alltext_normalized, "")

    def test_has_text(self):
        container = uicontainer.blocklist.BlocklistItemTitle(html_tag="h1", text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("h1").alltext_normalized, "test")


class TestBlocklistItem(test.TestCase):
    def test_sanity(self):
        container = uicontainer.blocklist.BlocklistItem().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("div"))

    def test_default_css_classes(self):
        container = uicontainer.blocklist.BlocklistItem().bootstrap()
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            selector = htmls.S(container.render())
        self.assertEqual(selector.one("div")["class"], "blocklist__item")

    def test_no_text(self):
        container = uicontainer.blocklist.BlocklistItem().bootstrap()
        selector = htmls.S(container.render())
        self.assertFalse(selector.exists("div p"))

    def test_has_text(self):
        container = uicontainer.blocklist.BlocklistItem(text="test").bootstrap()
        selector = htmls.S(container.render())
        self.assertEqual(selector.one("div p").alltext_normalized, "test")


class TestBlocklist(test.TestCase):
    def test_sanity(self):
        container = uicontainer.blocklist.Blocklist().bootstrap()
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists("div"))

    def test_default_css_classes(self):
        container = uicontainer.blocklist.Blocklist().bootstrap()
        with self.settings(DJANGO_CRADMIN_INCLUDE_TEST_CSS_CLASSES=False):
            selector = htmls.S(container.render())
        self.assertEqual(selector.one("div")["class"], "blocklist")

    def test_with_children(self):
        container = uicontainer.blocklist.Blocklist(
            children=[
                uicontainer.blocklist.BlocklistItem(text="a"),
                uicontainer.blocklist.BlocklistItem(text="b"),
            ]
        ).bootstrap()
        selector = htmls.S(container.render())
        child_text = [child.alltext_normalized for child in selector.list(".blocklist__item")]
        self.assertEqual(child_text[0], "a")
        self.assertEqual(child_text[1], "b")
