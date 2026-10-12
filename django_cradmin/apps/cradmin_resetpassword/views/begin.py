from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _, gettext_lazy
from django_cradmin import uicontainer
from django_cradmin.apps.cradmin_email import emailutils
from django_cradmin.apps.cradmin_generic_token_with_metadata.models import (
    GenericTokenWithMetadata,
    get_expiration_datetime_for_app,
)
from django_cradmin.viewhelpers import formview


class PasswordResetEmail(emailutils.AbstractEmail):
    subject_template = "cradmin_resetpassword/email/subject.django.txt"
    html_message_template = "cradmin_resetpassword/email/html_message.django.html"

    def get_context_data(self):
        context = super(PasswordResetEmail, self).get_context_data()
        context.update({"DJANGO_CRADMIN_SITENAME": settings.DJANGO_CRADMIN_SITENAME})
        return context


class EmailForm(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data["email"]
        user_model = get_user_model()
        if not user_model.objects.filter(email=email).exists():
            raise forms.ValidationError(_("No account with this email address found"))
        return email


class BeginPasswordResetView(formview.StandaloneFormView):
    template_name = "cradmin_resetpassword/begin.django.html"
    form_class = EmailForm

    def get_form_renderable(self):
        formchildren = [
            uicontainer.fieldwrapper.FieldWrapper(
                fieldname="email",
                field_renderable=uicontainer.field.Field(autofocus=True, placeholder=gettext_lazy("Email")),
            ),
            uicontainer.button.SubmitPrimary(text=gettext_lazy("Search")),
        ]
        return uicontainer.layout.AdminuiPageSectionTight(
            children=[
                uicontainer.form.Form(
                    form=self.get_form(), children=formchildren, dom_id="id_django_cradmin_resetpassword_begin_form"
                )
            ]
        ).bootstrap()

    def get_success_url(self):
        return reverse("cradmin-resetpassword-email-sent")

    def __send_email(self, user, reset_url):
        PasswordResetEmail(
            recipient=user.email,
            from_email=getattr(settings, "DJANGO_CRADMIN_RESETPASSWORD_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL),
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
        return super(BeginPasswordResetView, self).form_valid(form)
