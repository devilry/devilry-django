import htmls
from django import test
from django_cradmin import uicontainer


class TestMessagesContainer(test.TestCase):
    def test_do_not_render_if_empty(self):
        container = uicontainer.messagescontainer.MessagesContainer(
            test_css_class_suffixes_list=["messages"]
        ).bootstrap()
        selector = htmls.S(container.render())
        self.assertFalse(selector.exists(".test-messages"))

    def test_render_if_not_empty(self):
        container = (
            uicontainer.messagescontainer.MessagesContainer(test_css_class_suffixes_list=["messages"])
            .add_info(text="test")
            .bootstrap()
        )
        selector = htmls.S(container.render())
        self.assertTrue(selector.exists(".test-messages"))

    def test_css_classes_default(self):
        container = (
            uicontainer.messagescontainer.MessagesContainer(test_css_class_suffixes_list=["messages"])
            .add_info(text="test")
            .bootstrap()
        )
        selector = htmls.S(container.render())
        self.assertEqual(selector.one(".test-messages").cssclasses_set, {"test-messages", "messages"})

    def test_add_message(self):
        container = (
            uicontainer.messagescontainer.MessagesContainer(test_css_class_suffixes_list=["messages"])
            .add_message(level="info", text="test")
            .bootstrap()
        )
        selector = htmls.S(container.render())
        self.assertEqual(selector.one(".message").alltext_normalized, "test")

    def test_add_warning(self):
        container = (
            uicontainer.messagescontainer.MessagesContainer(test_css_class_suffixes_list=["messages"])
            .add_warning(text="test")
            .bootstrap()
        )
        selector = htmls.S(container.render())
        self.assertEqual(selector.one(".message.message--error").alltext_normalized, "test")

    def test_add_success(self):
        container = (
            uicontainer.messagescontainer.MessagesContainer(test_css_class_suffixes_list=["messages"])
            .add_success(text="test")
            .bootstrap()
        )
        selector = htmls.S(container.render())
        self.assertEqual(selector.one(".message.message--info").alltext_normalized, "test")

    def test_add_info(self):
        container = (
            uicontainer.messagescontainer.MessagesContainer(test_css_class_suffixes_list=["messages"])
            .add_info(text="test")
            .bootstrap()
        )
        selector = htmls.S(container.render())
        self.assertEqual(selector.one(".message.message--info").alltext_normalized, "test")
