import htmls
from unittest import mock
from django import test
from django import forms

from cradmin_legacy.viewhelpers.multiselect2 import target_renderer


class TestTarget(test.TestCase):
    def test_dom_id_default(self):
        selector = htmls.S(target_renderer.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual("cradmin_legacy_multiselect2_select_target", selector.one("form")["id"])

    def test_dom_id_custom(self):
        selector = htmls.S(
            target_renderer.Target(dom_id="customid", form=forms.Form()).render(request=mock.MagicMock())
        )
        self.assertEqual("customid", selector.one("form")["id"])

    def test_form_action_default(self):
        mockrequest = mock.MagicMock()
        mockrequest.get_full_path.return_value = "/form/action"
        selector = htmls.S(target_renderer.Target(form=forms.Form()).render(request=mockrequest))
        self.assertEqual("/form/action", selector.one("form")["action"])

    def test_form_action_custom_parameter(self):
        selector = htmls.S(
            target_renderer.Target(form_action="/some/view", form=forms.Form()).render(request=mock.MagicMock())
        )
        self.assertEqual("/some/view", selector.one("form")["action"])

    def test_form_action_override(self):
        class MyTarget(target_renderer.Target):
            def get_form_action(self, request):
                return "/custom"

        selector = htmls.S(MyTarget(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual("/custom", selector.one("form")["action"])

    def test_without_items_text_default(self):
        selector = htmls.S(target_renderer.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual(
            "", selector.one(".cradmin-legacy-multiselect2-target-without-items-content").alltext_normalized
        )

    def test_without_items_text_custom_parameter(self):
        selector = htmls.S(
            target_renderer.Target(without_items_text="Please make a selection", form=forms.Form()).render(
                request=mock.MagicMock()
            )
        )
        self.assertEqual(
            "Please make a selection",
            selector.one(".cradmin-legacy-multiselect2-target-without-items-content").alltext_normalized,
        )

    def test_without_items_text_override(self):
        class MyTarget(target_renderer.Target):
            def get_without_items_text(self):
                return "No items selected"

        selector = htmls.S(MyTarget(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual(
            "No items selected",
            selector.one(".cradmin-legacy-multiselect2-target-without-items-content").alltext_normalized,
        )

    def test_with_items_title_default(self):
        selector = htmls.S(target_renderer.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual("Selected items", selector.one(".cradmin-legacy-multiselect2-target-title").alltext_normalized)

    def test_with_items_title_custom_parameter(self):
        selector = htmls.S(
            target_renderer.Target(with_items_title="Test title", form=forms.Form()).render(request=mock.MagicMock())
        )
        self.assertEqual("Test title", selector.one(".cradmin-legacy-multiselect2-target-title").alltext_normalized)

    def test_with_items_title_override(self):
        class MyTarget(target_renderer.Target):
            def get_with_items_title(self):
                return "Test title"

        selector = htmls.S(MyTarget(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual("Test title", selector.one(".cradmin-legacy-multiselect2-target-title").alltext_normalized)

    def test_submit_button_text_default(self):
        selector = htmls.S(target_renderer.Target(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual("Submit selection", selector.one('button[type="submit"]').alltext_normalized)

    def test_submit_button_text_custom_parameter(self):
        selector = htmls.S(
            target_renderer.Target(submit_button_text="Perform", form=forms.Form()).render(request=mock.MagicMock())
        )
        self.assertEqual("Perform", selector.one('button[type="submit"]').alltext_normalized)

    def test_submit_button_text_override(self):
        class MyTarget(target_renderer.Target):
            def get_submit_button_text(self):
                return "Test text"

        selector = htmls.S(MyTarget(form=forms.Form()).render(request=mock.MagicMock()))
        self.assertEqual("Test text", selector.one('button[type="submit"]').alltext_normalized)


class TestManyToManySelectTarget(test.TestCase):
    def test_button_angularjs_directive(self):
        selector = htmls.S(
            target_renderer.ManyToManySelectTarget(target_formfield_id="testid", form=forms.Form()).render(
                request=mock.MagicMock()
            )
        )
        self.assertEqual('{"fieldid": "testid"}', selector.one("button")["cradmin-legacy-multiselect2-use-this"])
