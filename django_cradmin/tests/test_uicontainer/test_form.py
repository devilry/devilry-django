import htmls
import mock
from django import forms
from django import test
from django_cradmin import uicontainer


class MinimalForm(forms.Form):
    name = forms.CharField()


class TestFormRenderable(test.TestCase):
    def ttest_example(self):
        class ExampleForm(forms.Form):
            name = forms.CharField()
            age = forms.IntegerField()
            created_by = forms.CharField()
            user_type = forms.ChoiceField(
                choices=[
                    ("a", "A"),
                    ("b", "B"),
                ],
                initial="b",
                widget=forms.RadioSelect(),
            )

        form = ExampleForm()
        formrenderable = uicontainer.form.Form(
            form=form,
            children=[
                uicontainer.layout.AdminuiPageSectionTight(
                    children=[
                        uicontainer.fieldwrapper.FieldWrapper(
                            fieldname="name",
                            field_renderable=uicontainer.field.Field(autofocus=True, placeholder="The name ffs..."),
                        ),
                        uicontainer.fieldwrapper.FieldWrapper(fieldname="age"),
                        uicontainer.fieldwrapper.FieldWrapper(fieldname="user_type"),
                    ]
                ),
                uicontainer.layout.AdminuiPageSection(
                    bem_variant_list=["supertight"],
                    children=[
                        uicontainer.fieldwrapper.FieldWrapper(fieldname="created_by"),
                        uicontainer.fieldset.FieldSet(
                            title="Metadata",
                            children=[
                                uicontainer.fieldwrapper.FieldWrapper(fieldname="created_by"),
                            ],
                        ),
                    ],
                ),
                uicontainer.fieldwrapper.FieldWrapper(
                    fieldname="user_type",
                    field_renderable=uicontainer.field.Field(
                        subwidget_renderable_kwargs={"bem_variant_list": ["inline"]}
                    ),
                ),
            ],
        ).bootstrap()
        htmls.S(formrenderable.render(request=mock.MagicMock())).prettyprint()

    def test_get_default_method(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm())
        self.assertEqual(formrenderable.get_default_method(), "POST")

    def test_method_default(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm())
        self.assertEqual(formrenderable.method, "POST")

    def test_method_override_default(self):
        class MyFormRenderable(uicontainer.form.Form):
            def get_default_method(self):
                return "GET"

        formrenderable = MyFormRenderable(form=MinimalForm())
        self.assertEqual(formrenderable.method, "GET")

    def test_method_overridden_with_kwarg(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm(), method="GET")
        self.assertEqual(formrenderable.method, "GET")

    def test_action_is_redirect_to_self_default(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm())
        self.assertEqual(formrenderable.action_is_redirect_to_self(), True)

    def test_action_is_redirect_to_self_action_kwarg_none(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm(), action=None)
        self.assertEqual(formrenderable.action_is_redirect_to_self(), True)

    def test_action_is_redirect_to_self_action_kwarg_not_none(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm(), action="/test/submit")
        self.assertEqual(formrenderable.action_is_redirect_to_self(), False)

    def test_get_html_element_attributes_method(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm(), method="GET")
        self.assertEqual(formrenderable.get_html_element_attributes()["method"], "GET")

    def test_get_html_element_attributes_action_default(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm())
        # Not included by default - it is rendered by the template by default because
        # the default uses request.get_full_path()
        self.assertNotIn("action", formrenderable.get_html_element_attributes())

    def test_get_html_element_attributes_action_kwarg(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm(), action="/test/submit")
        self.assertEqual(formrenderable.get_html_element_attributes()["action"], "/test/submit")

    def test_register_field_wrapper_renderable(self):
        mock_field_wrapper_renderable = mock.MagicMock()
        mock_field_wrapper_renderable.fieldname = "test"
        formrenderable = uicontainer.form.Form(form=MinimalForm())
        formrenderable.register_field_wrapper_renderable(field_wrapper_renderable=mock_field_wrapper_renderable)
        self.assertEqual(formrenderable._fieldrenderable_map["test"], mock_field_wrapper_renderable)

    def test_get_field_wrapper_renderable(self):
        mock_field_wrapper_renderable = mock.MagicMock()
        mock_field_wrapper_renderable.fieldname = "test"
        formrenderable = uicontainer.form.Form(form=MinimalForm())
        formrenderable.register_field_wrapper_renderable(field_wrapper_renderable=mock_field_wrapper_renderable)
        self.assertEqual(formrenderable.get_field_wrapper_renderable("test"), mock_field_wrapper_renderable)

    def test_iter_field_wrapper_renderables(self):
        mock_field_wrapper_renderable1 = mock.MagicMock()
        mock_field_wrapper_renderable1.fieldname = "test1"
        mock_field_wrapper_renderable2 = mock.MagicMock()
        mock_field_wrapper_renderable2.fieldname = "test2"
        formrenderable = uicontainer.form.Form(form=MinimalForm())
        formrenderable.register_field_wrapper_renderable(field_wrapper_renderable=mock_field_wrapper_renderable1)
        formrenderable.register_field_wrapper_renderable(field_wrapper_renderable=mock_field_wrapper_renderable2)
        field_wrapper_renderables = list(formrenderable.iter_field_wrapper_renderables())
        self.assertIn(mock_field_wrapper_renderable1, field_wrapper_renderables)
        self.assertIn(mock_field_wrapper_renderable2, field_wrapper_renderables)

    def __make_mockrequest(self):
        mockrequest = mock.MagicMock()

        def getitem(me, key):
            return {"get_full_path": "/request-full-path"}.get(key, None)

        mockrequest.__getitem__ = getitem
        return mockrequest

    def test_render_wrappertag(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm()).bootstrap()
        selector = htmls.S(formrenderable.render(request=self.__make_mockrequest()))
        self.assertTrue(selector.exists("form"))

    def test_render_action_default(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm()).bootstrap()
        selector = htmls.S(formrenderable.render(request=self.__make_mockrequest()))
        self.assertEqual(selector.one("form")["action"], "/request-full-path")

    def test_render_action_kwarg_false(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm(), action=False).bootstrap()
        selector = htmls.S(formrenderable.render(request=self.__make_mockrequest()))
        self.assertFalse(selector.one("form").hasattribute("action"))

    def test_render_action_kwarg_string(self):
        formrenderable = uicontainer.form.Form(form=MinimalForm(), action="/overridden").bootstrap()
        selector = htmls.S(formrenderable.render(request=self.__make_mockrequest()))
        self.assertEqual(selector.one("form")["action"], "/overridden")

    def test_form_invalid_global_error(self):
        class TestForm(forms.Form):
            name = forms.CharField(required=False)

            def clean(self):
                raise forms.ValidationError("Global error test")

        form = TestForm(data={})
        formrenderable = uicontainer.form.Form(form=form).bootstrap()
        selector = htmls.S(formrenderable.render(request=self.__make_mockrequest()))
        self.assertEqual(
            selector.one(".test-form-globalmessages .test-warning-message").alltext_normalized, "Global error test"
        )

    def test_form_invalid_field_error(self):
        class TestForm(forms.Form):
            name = forms.CharField(required=True)

        form = TestForm(data={})
        formrenderable = uicontainer.form.Form(
            form=form, children=[uicontainer.fieldwrapper.FieldWrapper(fieldname="name")]
        ).bootstrap()
        selector = htmls.S(formrenderable.render(request=self.__make_mockrequest()))
        self.assertEqual(
            selector.one("#id_name_wrapper .test-warning-message").alltext_normalized, "This field is required."
        )

    def test_form_invalid_field_error_field_not_rendered_without_label(self):
        class TestForm(forms.Form):
            name = forms.CharField(required=True)

        form = TestForm(data={})
        formrenderable = uicontainer.form.Form(form=form).bootstrap()
        selector = htmls.S(formrenderable.render(request=self.__make_mockrequest()))
        self.assertEqual(
            selector.one(".test-form-globalmessages .test-warning-message").alltext_normalized,
            "name: This field is required.",
        )

    def test_form_invalid_field_error_field_not_rendered_with_label(self):
        class TestForm(forms.Form):
            name = forms.CharField(required=True, label="The name")

        form = TestForm(data={})
        formrenderable = uicontainer.form.Form(form=form).bootstrap()
        selector = htmls.S(formrenderable.render(request=self.__make_mockrequest()))
        self.assertEqual(
            selector.one(".test-form-globalmessages .test-warning-message").alltext_normalized,
            "The name: This field is required.",
        )
