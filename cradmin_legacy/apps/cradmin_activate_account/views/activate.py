from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from django_cradmin.apps.cradmin_generic_token_with_metadata.models import (
    GenericTokenWithMetadata,
    GenericTokenExpiredError,
)


class ActivateAccountView(TemplateView):
    template_name = "cradmin_activate_account/activate.django.html"
    appname = "cradmin_activate_account"

    #: The template used to render the success message.
    #: Default value for :obj:`~.ActivateAccountView.get_success_message_template`
    success_message_template = "cradmin_activate_account/messages/success.django.html"

    def get(self, *args, **kwargs):
        self.token_does_not_exist = False
        self.token_expired = False
        try:
            token = GenericTokenWithMetadata.objects.get_and_validate(token=self.kwargs["token"], app=self.appname)
        except GenericTokenWithMetadata.DoesNotExist:
            self.token_does_not_exist = True
        except GenericTokenExpiredError:
            self.token_expired = True
        else:
            return self.token_is_valid(token)
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["token_does_not_exist"] = self.token_does_not_exist
        context["token_expired"] = self.token_expired
        return context

    def get_success_message_template(self):
        """
        Get the template used to render the success message.
        Defaults to :obj:`~.ActivateAccountView.success_message_template`.
        """
        return self.success_message_template

    def get_success_message(self, user):
        """
        Get the success message added by :meth:`.add_success_message`.

        Defaults to rendering the :meth:`.get_success_message_template`
        template.
        """
        return render_to_string(self.get_success_message_template(), {"user": user}).strip()

    def add_success_message(self, user):
        """
        Add success message.

        Defaults to adding the value of :meth:`~.ActivateAccountView.get_success_message`
        as a django messages framework success message.
        """
        messages.success(self.request, self.get_success_message(user))

    def activate_user(self, user):
        """
        Activate the user.

        You can override this to provide custom user activation code,
        but you will most likely want to override the ``activate_user()``
        method of your User model if you have a custom user model.
        """
        if hasattr(user, "activate_user"):
            user.activate_user()
        else:
            user.is_active = True
        user.save()

    def token_is_valid(self, token):
        user = token.content_object
        next_url = token.metadata["next_url"]
        self.activate_user(user)
        self.add_success_message(user)
        return HttpResponseRedirect(next_url)
