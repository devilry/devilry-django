import datetime

from django import forms
from django.contrib import messages

from django_cradmin import uicontainer
from django_cradmin import viewhelpers


class ComplexForm(forms.Form):
    name = forms.CharField(required=False)
    boolean_field = forms.BooleanField(required=False, initial=False)
    birth_date = forms.DateField(required=False)
    disabled_datetime = forms.DateTimeField(required=False)
    my_time_field = forms.TimeField(required=False)
    select_something = forms.ChoiceField(required=False, choices=[(1, "Foo"), (2, "Bar")])
    select_something_else = forms.ChoiceField(
        required=False, choices=[(1, "Choice 1"), (2, "Choice2"), (2, "Choice3")], widget=forms.RadioSelect()
    )
    select_multiple = forms.TypedMultipleChoiceField(
        required=False,
        coerce=int,
        choices=[(1, "Choice 1"), (2, "Choice2"), (2, "Choice3")],
        widget=forms.CheckboxSelectMultiple(),
    )


class ComplextUiFormsView(viewhelpers.formview.WithinRoleFormView):
    form_class = ComplexForm

    def get_pagetitle(self):
        return "Simple uicontainer demo"

    def get_initial(self):
        return {
            "birth_date": datetime.date(2016, 3, 1),
            "disabled_datetime": datetime.datetime(2019, 12, 24, 18, 20),
            "my_time_field": datetime.time(2, 9),
        }

    def get_form_renderable(self):
        return uicontainer.form.Form(
            form=self.get_form(),
            children=[
                uicontainer.layout.AdminuiPageSectionTight(
                    children=[
                        # Almost the same as the simple_uiforms demo - but we
                        # add autofocus!
                        uicontainer.fieldwrapper.FieldWrapper(
                            fieldname="name", field_renderable=uicontainer.field.Field(autofocus=True)
                        ),
                        # Boolean fields are supported by the default field renderable.
                        uicontainer.fieldwrapper.FieldWrapper(fieldname="boolean_field"),
                        # Date field requires the Date field renderable to become
                        # usable. This has the added benefit of making it easy to
                        # create your own date field renderables, or just extend
                        # the default Date field renderable.
                        uicontainer.fieldwrapper.FieldWrapper(
                            fieldname="birth_date", field_renderable=uicontainer.field.Date()
                        ),
                        # Mostly the same as the date field above, but this
                        # time with DateTime field renderable
                        uicontainer.fieldwrapper.FieldWrapper(
                            fieldname="disabled_datetime", field_renderable=uicontainer.field.DateTime()
                        ),
                        # Mostly the same as the date field above, but this
                        # time with Time field renderable
                        uicontainer.fieldwrapper.FieldWrapper(
                            fieldname="my_time_field", field_renderable=uicontainer.field.Time()
                        ),
                        # Render the select_something field using the
                        # select renderable
                        uicontainer.fieldwrapper.FieldWrapper(
                            fieldname="select_something", field_renderable=uicontainer.field.Select()
                        ),
                        # Render the select_something_else field
                        # with the default field renderable - this handles
                        # the RadioSelect widget
                        uicontainer.fieldwrapper.FieldWrapper(fieldname="select_something_else"),
                        # Render the select_something_multiple field
                        # with the default field renderable - this handles
                        # the CheckboxSelectMultiple widget
                        uicontainer.fieldwrapper.FieldWrapper(fieldname="select_multiple"),
                        # We need a submit button :)
                        uicontainer.button.SubmitPrimary(text="Submit form"),
                    ]
                )
            ],
        ).bootstrap()

    # def get_javascriptregistry_component_ids(self):
    #     return ['django_cradmin_javascript']

    def form_invalid(self, form):
        return super(ComplextUiFormsView, self).form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, "Submitted data: {!r}".format(form.cleaned_data))
        return self.render_to_response(self.get_context_data(form=form))
