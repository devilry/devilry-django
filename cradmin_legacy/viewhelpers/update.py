from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy
from django.views.generic import UpdateView as DjangoUpdateView

from cradmin_legacy.crispylayouts import PrimarySubmit
from cradmin_legacy.crispylayouts import DefaultSubmit
from .crudbase import CreateUpdateViewMixin
from cradmin_legacy.viewhelpers.mixins import QuerysetForRoleMixin


class UpdateView(QuerysetForRoleMixin, CreateUpdateViewMixin, DjangoUpdateView):
    template_name = "cradmin_legacy/viewhelpers/update.django.html"

    def get_pagetitle(self):
        """
        Get the page title (the title tag).

        Defaults to ``Edit <verbose_name model>``.
        """
        return gettext_lazy("Edit %(what)s") % {"what": self.get_model_class()._meta.verbose_name}

    def get_buttons(self):
        buttons = [
            PrimarySubmit(self.get_submit_save_button_name(), self.get_submit_save_label()),
            DefaultSubmit(
                self.get_submit_save_and_continue_edititing_button_name(),
                self.get_submit_save_and_continue_edititing_label(),
            ),
        ]
        self.add_preview_button_if_configured(buttons)
        return buttons

    def get_formhelper(self):
        helper = super().get_formhelper()
        helper.form_id = "cradmin_legacy_updateform"
        return helper

    def get_success_message(self, object):
        return gettext_lazy('Saved "%(object)s".') % {"object": object}


class UpdateRoleView(UpdateView):
    """
    Extends :class:`.UpdateView` to streamline editing the current role
    object.

    Just like :class:`.UpdateView`, but with the get_object and
    get_queryset_for_role methods implemented to edit the current role
    object.
    """

    def get_object(self, queryset=None):
        return self.get_queryset_for_role(self.request.cradmin_role).get()

    def get_queryset_for_role(self, role):
        return self.get_model_class().objects.filter(pk=role.pk)


class RedirectToCreateIfDoesNotExistMixin:
    """
    An update view mixin that redirects to a create view when the
    object requested does not exist.

    You will typically use this for objects with a OneToOne relationship
    to the current role, but that may not exist. Then you would use
    something like::

        class MyUpdateView(update.UpdateView, update.RedirectToCreateIfDoesNotExistMixin):
            def get_object(self, queryset=None):
                return self.get_queryset_for_role(self.request.cradmin_role).get()

            def get_queryset_for_role(self, role):
                return self.get_model_class().objects.filter(someonetooneattr=role)

    And the view will automatically redirect to the create view
    if the object does not exist.
    """

    #: The viewname within this app for the create view.
    #: See :meth:`.get_createurl`. Defaults to ``create``.
    createview_appurl_name = "create"

    def get_createurl(self):
        """
        Get the URL of the create view that you want to redirect to if
        the requested object does not exist.

        Defaults to::

            self.request.cradmin_app.reverse_appurl(self.createview_appurl_name)
        """
        return self.request.cradmin_app.reverse_appurl(self.createview_appurl_name)

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except self.get_model_class().DoesNotExist:
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl("create"))
