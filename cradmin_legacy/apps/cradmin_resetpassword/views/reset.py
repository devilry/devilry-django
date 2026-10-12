from crispy_forms import layout
from crispy_forms.helper import FormHelper
from django.conf import settings
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy
from django import forms
from django.views.generic import FormView

from django_cradmin.apps.cradmin_generic_token_with_metadata.models import (
    GenericTokenWithMetadata,
    GenericTokenExpiredError,
)
from cradmin_legacy.crispylayouts import PrimarySubmitLg


class RepeatPasswordForm(forms.Form):
    password1 = forms.CharField(label=gettext_lazy("Type your new password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=gettext_lazy("Type your new password one more time"), widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(gettext_lazy("The passwords do not match"))


class ResetPasswordView(FormView):
    template_name = "cradmin_resetpassword/reset.django.html"
    form_class = RepeatPasswordForm

    def get_formhelper(self):
        helper = FormHelper()
        helper.form_action = "#"
        helper.form_id = "cradmin_legacy_resetpassword_reset_form"
        helper.layout = layout.Layout(
            layout.Field("password1", focusonme="focusonme", css_class="input-lg"),
            layout.Field("password2", css_class="input-lg"),
            PrimarySubmitLg("submit", gettext_lazy("Reset password")),
        )
        return helper

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formhelper"] = self.get_formhelper()
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
        return str(getattr(settings, "CRADMIN_LEGACY_RESETPASSWORD_FINISHED_REDIRECT_URL", settings.LOGIN_URL))

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
            return super().form_valid(form)
