import sys
import urllib.parse

from django.utils.translation import gettext_lazy
from django.views.generic import CreateView as DjangoCreateView

from cradmin_legacy.crispylayouts import DefaultSubmit, PrimarySubmit

from .crudbase import CreateUpdateViewMixin


class CreateView(CreateUpdateViewMixin, DjangoCreateView):
    template_name = "cradmin_legacy/viewhelpers/create.django.html"

    #: If this is ``True`` (default), we go into foreignkey select mode
    #: if ``foreignkey_select_mode=1`` is in the querystring.
    #:
    #: Foreignkey select mode:
    #:
    #: - replaces the normal save buttons with a ``submit-use`` button.
    #: - removes the menu (sets the ``cradmin_hide_menu`` template context variable to ``True``).
    #: - adds a ``foreignkey_selected_value=<selected pk>`` to the querystring of the success url.
    allow_foreignkey_select = True

    #: The label of the back button in foreign key select mode.
    foreignkey_select_mode_backbutton_label = gettext_lazy("Back")

    submit_use_label = gettext_lazy("Create and select")
    submit_save_label = gettext_lazy("Create")
    submit_save_and_continue_edititing_label = gettext_lazy("Create and continue editing")

    def get_pagetitle(self):
        """
        Get the page title (the title tag).

        Defaults to ``Create <verbose_name model>``.
        """
        return gettext_lazy("Create %(what)s") % {"what": self.get_model_class()._meta.verbose_name}

    def get_submit_use_label(self):
        """
        Get the "Create and select" label.

        Defaults to :obj:`~.FormViewMixin.submit_use_label`.
        """
        return self.submit_use_label

    def __get_foreignkey_select_mode_backbutton_url(self):
        """
        Get the URL of the back button in foreign key select mode.
        """
        return self.request.GET.get("success_url", "")

    def get_foreignkey_select_mode_backbutton_label(self):
        return self.foreignkey_select_mode_backbutton_label

    def get_buttons(self):
        if self.is_in_foreignkey_select_mode():
            buttons = [
                PrimarySubmit("submit-use", self.get_submit_use_label()),
            ]
        else:
            buttons = [
                PrimarySubmit(self.get_submit_save_button_name(), self.get_submit_save_label()),
                DefaultSubmit(
                    self.get_submit_save_and_continue_edititing_button_name(),
                    self.get_submit_save_and_continue_edititing_label(),
                ),
            ]
        self.add_preview_button_if_configured(buttons)
        return buttons

    @classmethod
    def add_foreignkey_selected_value_to_url_querystring(cls, url, object_pk):
        url = urllib.parse.unquote_plus(url)
        urllist = list(urllib.parse.urlsplit(url))
        querystring = urllist[3]
        querydict = urllib.parse.parse_qs(querystring)
        querydict["foreignkey_selected_value"] = [str(object_pk)]
        urllist[3] = urllib.parse.urlencode(querydict, doseq=True)
        url = urllib.parse.urlunsplit(urllist)
        if sys.version_info[0] == 2:
            # For some reason, HttpRedirect requires unicode string to work
            # correctly on Python2, so we ensure that here.
            url = unicode(url)  # noqa
        return url

    def get_default_save_success_url(self):
        url = super().get_default_save_success_url()
        if self.is_in_foreignkey_select_mode():
            url = self.__class__.add_foreignkey_selected_value_to_url_querystring(url, self.object.pk)
        return url

    def get_formhelper(self):
        helper = super().get_formhelper()
        helper.form_id = "cradmin_legacy_createform"
        return helper

    def is_in_foreignkey_select_mode(self):
        return self.allow_foreignkey_select and self.request.GET.get("foreignkey_select_mode") == "1"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cradmin_hide_menu"] = self.is_in_foreignkey_select_mode()
        context["is_foreignkey_select_mode"] = self.is_in_foreignkey_select_mode()
        context["foreignkey_select_mode_backbutton_url"] = self.__get_foreignkey_select_mode_backbutton_url()
        context["foreignkey_select_mode_backbutton_label"] = self.get_foreignkey_select_mode_backbutton_label()
        return context

    def get_success_message(self, object):
        return gettext_lazy('Created "%(object)s".') % {"object": object}


class CreateLikeUpdateView(CreateView):
    """
    Create view that looks just like an update view to the
    user.

    You will want to use this when you have a situation
    where you want users to edit an item, but you need them
    to create the item if it does not exist. In that case,
    use this as the base class of your create view, and
    override the get-method of your update view to redirect
    the create view if the item does not exist::

        class UpdateView(update.UpdateView):
            def get(self, request, *args, **kwargs):
                try:
                    return super(UpdateView, self).get(request, *args, **kwargs)
                except self.get_model_class().DoesNotExist:
                    return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl('create'))

    The user will then be redirected to the create view, but it
    will behave the same (output the same submit labels, and the same
    success message)
    """

    submit_save_label = gettext_lazy("Save")
    submit_save_and_continue_edititing_label = gettext_lazy("Save and continue editing")

    def get_success_message(self, object):
        return gettext_lazy('Saved "%(object)s".') % {"object": object}
