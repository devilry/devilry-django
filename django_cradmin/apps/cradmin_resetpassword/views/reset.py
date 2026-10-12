from django import forms
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _, gettext_lazy
from django_cradmin import uicontainer
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import (
    GenericTokenWithMetadata,
    GenericTokenExpiredError,
)
from django_cradmin.viewhelpers import formview


class RepeatPasswordForm(forms.Form):
    password1 = forms.CharField(label=_("Type your new password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Type your new password one more time"), widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(RepeatPasswordForm, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(_("The passwords do not match"))


class ResetPasswordView(formview.StandaloneFormView):
    template_name = "cradmin_resetpassword/reset.django.html"
    form_class = RepeatPasswordForm

    def get_form_renderable(self):
        formchildren = [
            uicontainer.fieldwrapper.FieldWrapper(
                fieldname="password1",
                field_renderable=uicontainer.field.Field(
                    autofocus=True,
                ),
            ),
            uicontainer.fieldwrapper.FieldWrapper(
                fieldname="password2",
            ),
            uicontainer.button.SubmitPrimary(text=gettext_lazy("Set password")),
        ]
        return uicontainer.layout.AdminuiPageSectionTight(
            children=[
                uicontainer.form.Form(
                    form=self.get_form(), children=formchildren, dom_id="id_django_cradmin_resetpassword_reset_form"
                )
            ]
        ).bootstrap()

    def get_context_data(self, **kwargs):
        context = super(ResetPasswordView, self).get_context_data(**kwargs)
        try:
            context["generic_token_with_metadata"] = GenericTokenWithMetadata.objects.get_and_validate(
                token=self.kwargs["token"], app="cradmin_resetpassword"
            )
        except GenericTokenWithMetadata.DoesNotExist:
            context["generic_token_with_metadata"] = None
        except GenericTokenExpiredError:
            context["generic_token_with_metadata_is_expired"] = True
        return context

    def get_success_url(self):
        return str(getattr(settings, "DJANGO_CRADMIN_RESETPASSWORD_FINISHED_REDIRECT_URL", settings.LOGIN_URL))

    def __get_success_message(self):
        return render_to_string("cradmin_resetpassword/messages/successmessage.django.html").strip()

    def form_valid(self, form):
        try:
            token = GenericTokenWithMetadata.objects.pop(token=self.kwargs["token"], app="cradmin_resetpassword")
        except GenericTokenWithMetadata.DoesNotExist:
            return self.render_to_response(self.get_context_data())
        else:
            raw_password = form.cleaned_data["password1"]
            user = token.content_object
            user.set_password(raw_password)
            user.save()
            messages.success(self.request, self.__get_success_message())
            return super(ResetPasswordView, self).form_valid(form)
