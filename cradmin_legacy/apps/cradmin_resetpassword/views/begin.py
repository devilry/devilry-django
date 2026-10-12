from crispy_forms import layout
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy
from django import forms
from django.views.generic import FormView

from crispy_forms.helper import FormHelper

from cradmin_legacy.apps.cradmin_email import emailutils
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import (
    GenericTokenWithMetadata,
    get_expiration_datetime_for_app,
)
from cradmin_legacy.crispylayouts import PrimarySubmitLg


class PasswordResetEmail(emailutils.AbstractEmail):
    subject_template = "cradmin_resetpassword/email/subject.django.txt"
    html_message_template = "cradmin_resetpassword/email/html_message.django.html"

    def get_context_data(self):
        context = super().get_context_data()
        context.update({"CRADMIN_LEGACY_SITENAME": settings.CRADMIN_LEGACY_SITENAME})
        return context


class EmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data["email"]
        user_model = get_user_model()
        if not user_model.objects.filter(email=email).exists():
            raise forms.ValidationError(gettext_lazy("No account with this email address found"))
        return email


class BeginPasswordResetView(FormView):
    template_name = "cradmin_resetpassword/begin.django.html"
    form_class = EmailForm

    def get_formhelper(self):
        helper = FormHelper()
        helper.form_action = "#"
        helper.form_id = "cradmin_legacy_resetpassword_begin_form"
        helper.form_show_labels = False
        helper.layout = layout.Layout(
            layout.Field("email", css_class="input-lg", placeholder=gettext_lazy("Email"), focusonme="focusonme"),
            PrimarySubmitLg("submit", gettext_lazy("Search")),
        )
        return helper

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formhelper"] = self.get_formhelper()
        return context

    def get_success_url(self):
        return str(reverse("cradmin-resetpassword-email-sent"))

    def __send_email(self, user, reset_url):
        PasswordResetEmail(
            recipient=user.email,
            from_email=getattr(settings, "CRADMIN_LEGACY_RESETPASSWORD_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL),
            extra_context_data={"user": user, "reset_url": reset_url},
        ).send()

    def _generate_token(self, user):
        return GenericTokenWithMetadata.objects.generate(
            app="cradmin_resetpassword",
            content_object=user,
            expiration_datetime=get_expiration_datetime_for_app("cradmin_resetpassword"),
        ).token

    def __generate_reset_url(self, user):
        reset_url = reverse("cradmin-resetpassword-reset", kwargs={"token": self._generate_token(user)})
        return self.request.build_absolute_uri(reset_url)

    def get_user(self, email):
        user_model = get_user_model()
        return get_object_or_404(user_model, email=email)

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = self.get_user(email)
        reset_url = self.__generate_reset_url(user=user)
        self.__send_email(user=user, reset_url=reset_url)
        return super().form_valid(form)
