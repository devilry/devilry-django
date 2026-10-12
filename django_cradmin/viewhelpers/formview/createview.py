import urllib.parse

from django.utils.translation import gettext_lazy
from django.views.generic import CreateView as DjangoCreateView

from django_cradmin import javascriptregistry
from django_cradmin.viewhelpers.mixins import CommonCradminViewMixin
from . import create_update_view_mixin


class CreateViewMixin(create_update_view_mixin.CreateUpdateViewMixin):
    """
    Common mixin class for create views.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.formview.CreateViewMixin``.
    """

    #: The viewname within this app for the edit view.
    #: See :meth:`.get_editurl`.
    editview_appurl_name = "edit"

    def get_pagetitle(self):
        """
        Get the page title (the title tag).

        Defaults to ``Create <verbose_name model>``.
        """
        return gettext_lazy("Create %(what)s") % {"what": self.model_verbose_name}

    def get_success_message(self, obj):
        """
        Defaults to ``"Created "<str(obj)>".``
        """
        return gettext_lazy('Created "%(object)s"') % {"object": obj}

    def get_editurl(self, obj):
        """
        Get the edit URL for ``obj``.

        Defaults to::

            self.request.cradmin_app.reverse_appurl(self.editview_appurl_name, args=[obj.pk])

        You normally want to use :meth:`.get_full_editurl` instead of this method.
        """
        return self.request.cradmin_app.reverse_appurl(self.editview_appurl_name, args=[obj.pk])

    def get_full_editurl(self, obj):
        """
        Get the full edit URL for the provided object.

        Unlike :meth:`.get_editurl`, this ensures that any ``success_url`` in ``request.GET``
        is included in the URL.

        Args:
            obj: A saved model object.
        """
        url = self.get_editurl(obj)
        if "success_url" in self.request.GET:
            url = "{}?{}".format(url, urllib.parse.urlencode({"success_url": self.request.GET["success_url"]}))
        return url


class WithinRoleCreateView(
    CreateViewMixin, DjangoCreateView, CommonCradminViewMixin, javascriptregistry.viewmixin.WithinRoleViewMixin
):
    """
    Create view with the correct context data and sane base template
    for views where we have a cradmin role.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.formview.WithinRoleCreateView``.
    """

    template_name = "django_cradmin/viewhelpers/formview/within_role_create_view.django.html"

    def get_context_data(self, **kwargs):
        context = super(WithinRoleCreateView, self).get_context_data(**kwargs)
        self.add_javascriptregistry_component_ids_to_context(context=context)
        self.add_common_view_mixin_data_to_context(context=context)
        self.add_create_update_view_mixin_context_data(context=context)
        return context
