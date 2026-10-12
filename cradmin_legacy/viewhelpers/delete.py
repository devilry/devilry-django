from django.contrib import messages
from django.views.generic import DeleteView as DjangoDeleteView
from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers.mixins import QuerysetForRoleMixin


class DeleteView(QuerysetForRoleMixin, DjangoDeleteView):
    #: The name of the template to use.
    template_name = "cradmin_legacy/viewhelpers/delete.django.html"

    def get_pagetitle(self):
        """
        Get the page title (the title tag).

        Defaults to ``Delete <verbose_name model>``.
        """
        return gettext_lazy("Delete %(what)s") % {"what": self.get_object_preview()}

    def get_action_label(self):
        """
        The action we are performing.

        Used as the prefix of the page title (see :meth:`.get_pagetitle`),
        and as the default for :meth:`.get_delete_button_label`.
        """
        return gettext_lazy("Delete")

    def get_delete_button_label(self):
        """
        The label of the delete button.

        Defaults to :meth:`.get_action_label`.
        """
        return self.get_action_label()

    def get_object_preview(self):
        """
        The preview of the object. Used when asking the user if he/she wants to
        delete the current object.
        """
        obj = self.get_object()
        return str(obj)

    def get_confirm_message(self):
        """
        Get the confirm message shown in the focus area of the view.
        """
        return gettext_lazy('Are you sure you want to delete "%(object_preview)s"?') % {
            "object_preview": self.get_object_preview()
        }

    def get_success_url(self):
        """
        Get the URL to go to if object was deleted.

        Defaults to the INDEX view of the current app.
        """
        return str(self.request.cradmin_app.reverse_appindexurl())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = context["object"]
        context["model_verbose_name"] = obj._meta.verbose_name
        context["success_url"] = self.get_success_url()
        context["object_preview"] = self.get_object_preview()
        context["pagetitle"] = self.get_pagetitle()
        context["confirm_message"] = self.get_confirm_message()
        context["delete_button_label"] = self.get_delete_button_label()
        return context

    def get_success_message(self, object_preview):
        """
        Override this to provide a success message.

        Used by :meth:`.add_success_messages`.
        """
        return gettext_lazy('Deleted "%(what)s"') % {"what": object_preview}

    def add_success_messages(self, object_preview):
        """
        Called after the object has been deleted.

        Defaults to add :meth:`.get_success_message` as a django messages
        success message if :meth:`.get_success_message` returns anything.

        You can override this to add multiple messages or to show messages in some other way.
        """
        success_message = self.get_success_message(object_preview)
        if success_message:
            messages.success(self.request, success_message)

    def delete(self, request, *args, **kwargs):
        object_preview = self.get_object_preview()
        response = super().delete(request, *args, **kwargs)
        self.add_success_messages(object_preview)
        return response
