import htmls
from django import test
from django.http import QueryDict

from cradmin_legacy import python2_compatibility
from cradmin_legacy.python2_compatibility import mock
from cradmin_legacy.viewhelpers.multiselect2 import manytomanywidget


class TestWidget(test.TestCase):
    def test_wrapper_div_id(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertTrue(selector.exists("#id_cradmin_modelmultichoicefieldwrapper_testname"))

    def test_wrapper_class(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertTrue(
            selector.one("#id_cradmin_modelmultichoicefieldwrapper_testname").hasclass(
                "cradmin-legacy-modelmultichoicefield-wrapper"
            )
        )

    def test_wrapper_angularjs_directive_value(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=[1, 2], attrs={"id": "testid"}
            )
        )
        directive_value = selector.one("#id_cradmin_modelmultichoicefieldwrapper_testname")[
            "cradmin-legacy-model-choice-field-wrapper"
        ]
        path, querydictstring = directive_value.split("?")
        querydict = QueryDict(querydictstring)
        self.assertEqual("/test", path)
        self.assertEqual(
            {
                "manytomany_select_fieldid": "testid",
                "manytomany_select_current_value": "[1, 2]",
                "manytomany_select_required": "True",
            },
            querydict.dict(),
        )

    def test_inputfield_value_none(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertEqual("[]", selector.one('input[name="testname"]')["value"])

    def test_inputfield_value_empty_string(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value="", attrs={"id": "testid"}
            )
        )
        self.assertEqual("[]", selector.one('input[name="testname"]')["value"])

    def test_inputfield_value(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=[1, 2], attrs={"id": "testid"}
            )
        )
        self.assertEqual("[1, 2]", selector.one('input[name="testname"]')["value"])

    def test_inputfield_type_input_field_visible_default(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertEqual("hidden", selector.one('input[name="testname"]')["type"])

    def test_inputfield_type_input_field_visible_false(self):
        class MyWidget(manytomanywidget.Widget):
            input_field_visible = False

        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            MyWidget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertEqual("hidden", selector.one('input[name="testname"]')["type"])

    def test_inputfield_type_input_field_visible_true(self):
        class MyWidget(manytomanywidget.Widget):
            input_field_visible = True

        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            MyWidget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertEqual("text", selector.one('input[name="testname"]')["type"])

    def test_preview_list_sanity(self):
        mockqueryset = mock.MagicMock()
        mockqueryset.filter.return_value = []
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertTrue(selector.exists(".cradmin-legacy-multiselect2-preview-list"))

    def test_preview_list_angularjs_directive(self):
        mockqueryset = mock.MagicMock()
        mockqueryset.filter.return_value = []
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertTrue(
            selector.one(".cradmin-legacy-multiselect2-preview-list").hasattribute(
                "cradmin-legacy-model-choice-field-preview"
            )
        )

    def test_preview_list_without_value(self):
        mockqueryset = mock.MagicMock()
        mockqueryset.filter.return_value = []
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertEqual(0, selector.count(".cradmin-legacy-multiselect2-preview-list li"))

    def test_preview_list_with_value(self):
        mockqueryset = mock.MagicMock()
        mockmodelobject = mock.MagicMock()
        mockmodelobject.pk = 1
        mockmodelobject.__str__.return_value = "testvalue"
        if python2_compatibility.is_python2():
            mockmodelobject.__unicode__.return_value = "testvalue"
        mockqueryset.filter.return_value = [mockmodelobject]
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertEqual(1, selector.count(".cradmin-legacy-multiselect2-preview-list li"))
        self.assertEqual(
            "testvalue",
            selector.one(
                ".cradmin-legacy-multiselect2-preview-list .cradmin-legacy-multiselect2-preview-list-value"
            ).alltext_normalized,
        )

    def test_selectbutton_angularjs_directive(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertTrue(selector.one("button").hasattribute("cradmin-legacy-model-choice-field-changebegin-button"))

    def test_selectbutton_css_class(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertEqual("btn btn-default", selector.one("button")["class"])

    def test_selectbutton_text_default(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(queryset=mockqueryset, selectview_url="/test").render(
                name="testname", value=None, attrs={"id": "testid"}
            )
        )
        self.assertEqual("Select ...", selector.one("button").alltext_normalized)

    def test_selectbutton_text_custom(self):
        mockqueryset = mock.MagicMock()
        selector = htmls.S(
            manytomanywidget.Widget(
                queryset=mockqueryset, selectview_url="/test", selectbutton_text="Testing ..."
            ).render(name="testname", value=None, attrs={"id": "testid"})
        )
        self.assertEqual("Testing ...", selector.one("button").alltext_normalized)
