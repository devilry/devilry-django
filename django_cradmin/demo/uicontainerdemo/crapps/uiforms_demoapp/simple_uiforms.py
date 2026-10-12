from django import forms
from django.contrib import messages

from django_cradmin import uicontainer
from django_cradmin import viewhelpers


class SimpleForm(forms.Form):
    name = forms.CharField(required=False)


class SimpleUiFormsView(viewhelpers.formview.WithinRoleFormView):
    form_class = SimpleForm

    def get_pagetitle(self):
        return "Simple uicontainer demo"

    def get_form_renderable(self):
        return uicontainer.form.Form(
            form=self.get_form(),
            children=[
                uicontainer.layout.AdminuiPageSectionTight(
                    children=[
                        # Render the name field using defaults
                        uicontainer.fieldwrapper.FieldWrapper(fieldname="name"),
                        # Add a submit button to the form
                        uicontainer.button.SubmitPrimary(text="Submit form"),
                    ]
                )
            ],
        ).bootstrap()

    def form_valid(self, form):
        messages.success(self.request, "Submitted data: {!r}".format(form.cleaned_data))
        return self.render_to_response(self.get_context_data(form=form))
