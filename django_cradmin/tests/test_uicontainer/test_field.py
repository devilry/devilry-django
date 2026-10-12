from django import forms
from django import test
from django_cradmin import uicontainer

from . import formtest_mixins


class TestFieldBasics(test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin):
    def test_hiddenwidget_sanity(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField(widget=forms.HiddenInput()))
        self.assertEqual("hidden", selector.one('input[name="testfield"]')["type"])

    def test_placeholder_default(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField())
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("placeholder"))

    def test_placeholder_kwarg_false(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(),
            fieldwrapper=uicontainer.fieldwrapper.FieldWrapper(
                fieldname="testfield", field_renderable=uicontainer.field.Field(placeholder=False)
            ),
        )
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("placeholder"))

    def test_placeholder_kwarg_string(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(),
            fieldwrapper=uicontainer.fieldwrapper.FieldWrapper(
                fieldname="testfield", field_renderable=uicontainer.field.Field(placeholder="Type something")
            ),
        )
        self.assertEqual(selector.one('input[name="testfield"]')["placeholder"], "Type something")

    def test_autofocus_default(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField())
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("autofocus"))

    def test_autofocus_kwarg_false(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(),
            fieldwrapper=uicontainer.fieldwrapper.FieldWrapper(
                fieldname="testfield", field_renderable=uicontainer.field.Field(autofocus=False)
            ),
        )
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("autofocus"))

    def test_autofocus_kwarg_true(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(),
            fieldwrapper=uicontainer.fieldwrapper.FieldWrapper(
                fieldname="testfield", field_renderable=uicontainer.field.Field(autofocus=True)
            ),
        )
        self.assertTrue(selector.one('input[name="testfield"]').hasattribute("autofocus"))


class TestFieldCharFieldRendering(test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin):
    def test_charfield_name(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField())
        self.assertTrue(selector.exists('input[name="testfield"]'))

    def test_charfield_id(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField())
        self.assertEqual("id_testfield", selector.one('input[name="testfield"]')["id"])

    def test_charfield_type(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField())
        self.assertEqual("text", selector.one('input[name="testfield"]')["type"])

    def test_charfield_required(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField())
        self.assertTrue(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_charfield_not_required(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField(required=False))
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_charfield_widget_attrs(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(widget=forms.TextInput(attrs={"my-attribute": "10"}))
        )
        self.assertEqual("10", selector.one('input[name="testfield"]')["my-attribute"])

    def test_charfield_initial(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField(initial="testinitial"))
        self.assertEqual("testinitial", selector.one('input[name="testfield"]')["value"])

    def test_charfield_value_from_form(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField(), formvalue="testvalue")
        self.assertEqual("testvalue", selector.one('input[name="testfield"]')["value"])

    def test_css_classes_sanity(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField())
        self.assertEqual(
            selector.one('input[name="testfield"]').cssclasses_set,
            {"input", "input--outlined", "test-uicontainer-field", "test-djangowidget-textinput"},
        )


class TestFieldIntegerFieldRendering(test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin):
    def test_integerfield_name(self):
        selector = self.single_field_formrenderable_htmls(field=forms.IntegerField())
        self.assertTrue(selector.exists('input[name="testfield"]'))

    def test_integerfield_id(self):
        selector = self.single_field_formrenderable_htmls(field=forms.IntegerField())
        self.assertEqual("id_testfield", selector.one('input[name="testfield"]')["id"])

    def test_integerfield_type(self):
        selector = self.single_field_formrenderable_htmls(field=forms.IntegerField())
        self.assertEqual("number", selector.one('input[name="testfield"]')["type"])

    def test_integerfield_required(self):
        selector = self.single_field_formrenderable_htmls(field=forms.IntegerField())
        self.assertTrue(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_integerfield_not_required(self):
        selector = self.single_field_formrenderable_htmls(field=forms.IntegerField(required=False))
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_integerfield_widget_attrs(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.IntegerField(widget=forms.TextInput(attrs={"my-attribute": "10"}))
        )
        self.assertEqual("10", selector.one('input[name="testfield"]')["my-attribute"])

    def test_integerfield_initial(self):
        selector = self.single_field_formrenderable_htmls(field=forms.IntegerField(initial=10))
        self.assertEqual("10", selector.one('input[name="testfield"]')["value"])

    def test_integerfield_value_from_form(self):
        selector = self.single_field_formrenderable_htmls(field=forms.IntegerField(), formvalue=20)
        self.assertEqual("20", selector.one('input[name="testfield"]')["value"])

    def test_css_classes_sanity(self):
        selector = self.single_field_formrenderable_htmls(field=forms.IntegerField())
        self.assertEqual(
            selector.one('input[name="testfield"]').cssclasses_set,
            {"input", "input--outlined", "test-uicontainer-field", "test-djangowidget-numberinput"},
        )


class TestFieldTextareaRendering(test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin):
    def test_textarea_name(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField(widget=forms.Textarea()))
        self.assertTrue(selector.exists('textarea[name="testfield"]'))

    def test_textarea_id(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField(widget=forms.Textarea()))
        self.assertEqual("id_testfield", selector.one('textarea[name="testfield"]')["id"])

    def test_textarea_required(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField(widget=forms.Textarea()))
        self.assertTrue(selector.one('textarea[name="testfield"]').hasattribute("required"))

    def test_textarea_not_required(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(required=False, widget=forms.Textarea())
        )
        self.assertFalse(selector.one('textarea[name="testfield"]').hasattribute("required"))

    def test_textarea_widget_attrs(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(widget=forms.Textarea(attrs={"my-attribute": "10"}))
        )
        self.assertEqual("10", selector.one('textarea[name="testfield"]')["my-attribute"])

    def test_textarea_initial(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(initial="testinitial", widget=forms.Textarea())
        )
        self.assertEqual("testinitial", selector.one('textarea[name="testfield"]').alltext)

    def test_textarea_value_from_form(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(widget=forms.Textarea()), formvalue="testvalue"
        )
        self.assertEqual("testvalue", selector.one('textarea[name="testfield"]').alltext)

    def test_css_classes_sanity(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(widget=forms.Textarea()), formvalue="testvalue"
        )
        self.assertEqual(
            selector.one('textarea[name="testfield"]').cssclasses_set,
            {"input", "input--outlined", "test-uicontainer-field", "test-djangowidget-textarea"},
        )


class TestFieldBooleanFieldRendering(test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin):
    def test_booleanfield_name(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField())
        self.assertTrue(selector.exists('input[name="testfield"]'))

    def test_booleanfield_id(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField())
        self.assertEqual("id_testfield", selector.one('input[name="testfield"]')["id"])

    def test_booleanfield_type(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField())
        self.assertEqual("checkbox", selector.one('input[name="testfield"]')["type"])

    def test_booleanfield_required(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField())
        self.assertTrue(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_booleanfield_not_required(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField(required=False))
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_booleanfield_widget_attrs(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.BooleanField(widget=forms.TextInput(attrs={"my-attribute": "10"}))
        )
        self.assertEqual("10", selector.one('input[name="testfield"]')["my-attribute"])

    def test_booleanfield_initial_true(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField(initial=True))
        self.assertTrue(selector.one('input[name="testfield"]').hasattribute("checked"))

    def test_booleanfield_initial_false(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField(initial=False))
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("checked"))

    def test_booleanfield_value_from_form_true(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField(), formvalue=True)
        self.assertTrue(selector.one('input[name="testfield"]').hasattribute("checked"))

    def test_booleanfield_value_from_form_false(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField(), formvalue=False)
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("checked"))

    def test_css_classes_sanity(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField())
        self.assertEqual(
            selector.one('input[name="testfield"]').cssclasses_set,
            {"test-uicontainer-field", "test-djangowidget-checkboxinput"},
        )


class TestFieldChoiceFieldRendering(test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin):
    def test_choicefield_select_name(self):
        selector = self.single_field_formrenderable_htmls(field=forms.ChoiceField(choices=[("a", "A")]))
        self.assertTrue(selector.exists('select[name="testfield"]'))

    def test_choicefield_select_id(self):
        selector = self.single_field_formrenderable_htmls(field=forms.ChoiceField(choices=[("a", "A")]))
        self.assertEqual("id_testfield", selector.one('select[name="testfield"]')["id"])

    def test_choicefield_select_required(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(
                choices=[
                    # NOTE: Django 1.11+ does not render required unless the first option
                    #       has no value, since it is invalid HTML to have a select that
                    #       can not have blank value be required
                    ("", "A"),
                    ("b", "B"),
                ]
            )
        )
        self.assertTrue(selector.one('select[name="testfield"]').hasattribute("required"))

    def test_choicefield_select_not_required(self):
        selector = self.single_field_formrenderable_htmls(field=forms.ChoiceField(choices=[("a", "A")], required=False))
        self.assertFalse(selector.one('select[name="testfield"]').hasattribute("required"))

    def test_choicefield_select_widget_attrs(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A")], widget=forms.Select(attrs={"my-attribute": "10"}))
        )
        self.assertEqual("10", selector.one('select[name="testfield"]')["my-attribute"])

    def test_choicefield_select_initial(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A"), ("b", "B")], initial="b")
        )
        self.assertTrue(selector.one('select[name="testfield"] option[value="b"]').hasattribute("selected"))
        self.assertFalse(selector.one('select[name="testfield"] option[value="a"]').hasattribute("selected"))

    def test_choicefield_select_value_from_form(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A"), ("b", "B")]), formvalue="b"
        )
        self.assertTrue(selector.one('select[name="testfield"] option[value="b"]').hasattribute("selected"))
        self.assertFalse(selector.one('select[name="testfield"] option[value="a"]').hasattribute("selected"))

    def test_css_classes_sanity(self):
        selector = self.single_field_formrenderable_htmls(field=forms.ChoiceField(choices=[("a", "A")]))
        self.assertEqual(
            selector.one('select[name="testfield"]').cssclasses_set,
            {"test-uicontainer-field", "test-djangowidget-select"},
        )

    def test_not_wrapped_in_label(self):
        selector = self.single_field_formrenderable_htmls(field=forms.MultipleChoiceField(choices=[("a", "A")]))
        self.assertTrue(selector.exists("label"))
        self.assertTrue(selector.exists("select"))
        self.assertFalse(selector.exists("label select"))


class TestFieldChoiceFieldRadioWidgetRendering(test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin):
    def test_choicefield_radio_name(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A")], widget=forms.RadioSelect())
        )
        self.assertEqual(selector.count('input[name="testfield"]'), 1)

    def test_choicefield_radio_multiple(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A"), ("b", "B")], widget=forms.RadioSelect())
        )
        self.assertEqual(selector.count('input[name="testfield"]'), 2)

    def test_choicefield_radio_id(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A")], widget=forms.RadioSelect())
        )
        self.assertEqual("id_testfield_0", selector.one('input[name="testfield"]')["id"])

    def test_choicefield_radio_id_multiple(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A"), ("b", "B"), ("c", "C")], widget=forms.RadioSelect())
        )
        self.assertTrue(selector.exists("#id_testfield_0"))
        self.assertTrue(selector.exists("#id_testfield_1"))
        self.assertTrue(selector.exists("#id_testfield_2"))

    def test_choicefield_radio_required(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A")], widget=forms.RadioSelect(), required=True)
        )
        self.assertTrue(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_choicefield_radio_not_required(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A")], widget=forms.RadioSelect(), required=False)
        )
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_choicefield_radio_widget_attrs(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A")], widget=forms.RadioSelect(attrs={"my-attribute": "10"}))
        )
        self.assertEqual("10", selector.one('input[name="testfield"]')["my-attribute"])

    def test_choicefield_radio_initial(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A"), ("b", "B")], initial="b", widget=forms.RadioSelect())
        )
        self.assertFalse(selector.one('#id_testfield_wrapper input[value="a"]').hasattribute("checked"))
        self.assertTrue(selector.one('#id_testfield_wrapper input[value="b"]').hasattribute("checked"))

    def test_choicefield_radio_value_from_form(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A"), ("b", "B")], initial="b", widget=forms.RadioSelect()),
            formvalue="a",
        )
        self.assertTrue(selector.one('#id_testfield_wrapper input[value="a"]').hasattribute("checked"))
        self.assertFalse(selector.one('#id_testfield_wrapper input[value="b"]').hasattribute("checked"))

    def test_choicefield_radio_main_label_no_for(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.ChoiceField(choices=[("a", "A")], widget=forms.RadioSelect())
        )
        self.assertFalse(selector.one("#id_testfield_label").hasattribute("for"))


class TestFieldMultipleChoiceFieldRendering(test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin):
    def test_multichoicefield_name(self):
        selector = self.single_field_formrenderable_htmls(field=forms.MultipleChoiceField(choices=[("a", "A")]))
        self.assertTrue(selector.exists('select[name="testfield"]'))

    def test_multichoicefield_multiple(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A"), ("b", "B")])
        )
        self.assertEqual(selector.count('select[name="testfield"] option'), 2)

    def test_multichoicefield_id(self):
        selector = self.single_field_formrenderable_htmls(field=forms.MultipleChoiceField(choices=[("a", "A")]))
        self.assertEqual("id_testfield", selector.one('select[name="testfield"]')["id"])

    def test_multichoicefield_multipe_attribute(self):
        selector = self.single_field_formrenderable_htmls(field=forms.MultipleChoiceField(choices=[("a", "A")]))
        self.assertTrue(selector.one("#id_testfield").hasattribute("multiple"))

    def test_multichoicefield_id_multiple(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A"), ("b", "B"), ("c", "C")])
        )
        self.assertEqual(selector.count("#id_testfield option"), 3)

    def test_multichoicefield_required(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A")], required=True)
        )
        self.assertTrue(selector.one('select[name="testfield"]').hasattribute("required"))

    def test_multichoicefield_not_required(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A")], required=False)
        )
        self.assertFalse(selector.one('select[name="testfield"]').hasattribute("required"))

    def test_multichoicefield_widget_attrs(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(
                choices=[("a", "A")], widget=forms.SelectMultiple(attrs={"my-attribute": "10"})
            )
        )
        self.assertEqual("10", selector.one('select[name="testfield"]')["my-attribute"])

    def test_multichoicefield_initial(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A"), ("b", "B")], initial="b")
        )
        self.assertFalse(selector.one('#id_testfield option[value="a"]').hasattribute("selected"))
        self.assertTrue(selector.one('#id_testfield option[value="b"]').hasattribute("selected"))

    def test_multichoicefield_value_from_form(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A"), ("b", "B")], initial="b"), formvalue="a"
        )
        self.assertTrue(selector.one('#id_testfield option[value="a"]').hasattribute("selected"))
        self.assertFalse(selector.one('#id_testfield option[value="b"]').hasattribute("selected"))

    def test_multichoicefield_not_wrapped_in_label(self):
        selector = self.single_field_formrenderable_htmls(field=forms.MultipleChoiceField(choices=[("a", "A")]))
        self.assertTrue(selector.exists("label"))
        self.assertTrue(selector.exists("select"))
        self.assertFalse(selector.exists("label select"))


class TestFieldMultipleChoiceFieldCheckboxWidgetRendering(
    test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin
):
    def test_multichoicefield_checkbox_name(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A")], widget=forms.CheckboxSelectMultiple())
        )
        self.assertEqual(selector.count('input[name="testfield"]'), 1)

    def test_multichoicefield_checkbox_multiple(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A"), ("b", "B")], widget=forms.CheckboxSelectMultiple())
        )
        self.assertEqual(selector.count('input[name="testfield"]'), 2)

    def test_multichoicefield_checkbox_id(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A")], widget=forms.CheckboxSelectMultiple())
        )
        self.assertEqual("id_testfield_0", selector.one('input[name="testfield"]')["id"])

    def test_multichoicefield_checkbox_id_multiple(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(
                choices=[("a", "A"), ("b", "B"), ("c", "C")], widget=forms.CheckboxSelectMultiple()
            )
        )
        self.assertTrue(selector.exists("#id_testfield_0"))
        self.assertTrue(selector.exists("#id_testfield_1"))
        self.assertTrue(selector.exists("#id_testfield_2"))

    def test_multichoicefield_checkbox_required(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A")], widget=forms.CheckboxSelectMultiple(), required=True)
        )
        # NOTE: Multiple checkboxes can not have required attribute - they do not
        #       seem to be handled the same way as radio (in html5).
        #       This makes a bit of sense because what we mean by required in Django
        #       with required is that at least one must be checked, and HTML5
        #       required do not seem to use the same logic.
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_multichoicefield_checkbox_not_required(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A")], widget=forms.CheckboxSelectMultiple(), required=False)
        )
        self.assertFalse(selector.one('input[name="testfield"]').hasattribute("required"))

    def test_multichoicefield_checkbox_widget_attrs(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(
                choices=[("a", "A")], widget=forms.CheckboxSelectMultiple(attrs={"my-attribute": "10"})
            )
        )
        self.assertEqual("10", selector.one('input[name="testfield"]')["my-attribute"])

    def test_multichoicefield_checkbox_initial(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(
                choices=[("a", "A"), ("b", "B")], initial="b", widget=forms.CheckboxSelectMultiple()
            )
        )
        self.assertFalse(selector.one('#id_testfield_wrapper input[value="a"]').hasattribute("checked"))
        self.assertTrue(selector.one('#id_testfield_wrapper input[value="b"]').hasattribute("checked"))

    def test_multichoicefield_checkbox_value_from_form(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(
                choices=[("a", "A"), ("b", "B")], initial="b", widget=forms.CheckboxSelectMultiple()
            ),
            formvalue="a",
        )
        self.assertTrue(selector.one('#id_testfield_wrapper input[value="a"]').hasattribute("checked"))
        self.assertFalse(selector.one('#id_testfield_wrapper input[value="b"]').hasattribute("checked"))

    def test_multichoicefield_checkbox_main_label_no_for(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.MultipleChoiceField(choices=[("a", "A")], widget=forms.CheckboxSelectMultiple())
        )
        self.assertFalse(selector.one("#id_testfield_label").hasattribute("for"))


class TestHiddenField(test.TestCase, formtest_mixins.SingleFormRenderableHelperMixin):
    def single_field_formrenderable_fieldwrapper_factory(self):
        return uicontainer.fieldwrapper.FieldWrapper(
            fieldname="testfield", field_renderable=uicontainer.field.HiddenField()
        )

    def test_charfield_type(self):
        selector = self.single_field_formrenderable_htmls(field=forms.CharField())
        self.assertEqual("hidden", selector.one('input[name="testfield"]')["type"])

    def test_integerfield_type(self):
        selector = self.single_field_formrenderable_htmls(field=forms.IntegerField())
        self.assertEqual("hidden", selector.one('input[name="testfield"]')["type"])

    def test_textarea_type(self):
        selector = self.single_field_formrenderable_htmls(
            field=forms.CharField(initial="testinitial", widget=forms.Textarea())
        )
        self.assertEqual("hidden", selector.one('input[name="testfield"]')["type"])

    def test_booleanfield_type(self):
        selector = self.single_field_formrenderable_htmls(field=forms.BooleanField())
        self.assertEqual("hidden", selector.one('input[name="testfield"]')["type"])

    def test_choicefield_type(self):
        selector = self.single_field_formrenderable_htmls(field=forms.ChoiceField(choices=[("a", "A")]))
        self.assertEqual("hidden", selector.one('input[name="testfield"]')["type"])
