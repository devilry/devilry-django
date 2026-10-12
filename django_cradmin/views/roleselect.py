from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

from django_cradmin import javascriptregistry


class RoleSelectView(javascriptregistry.viewmixin.WithinRoleViewMixin, ListView):
    """
    The default view for listing and selecting roles within a cradmin instance.

    - If the user has a single role, we redirect to the role-frontpage for that role.
      This behavior can be overridden with :meth:`.get_autoredirect_if_single_role`.
    - If the user has multiple roles, we list the roles.
    - If the user has no roles, we call :meth:`.get_no_roles_response`.
    """

    paginate_by = 30

    #: Makes the roles queryset available as ``roles`` in the template.
    context_object_name = "roles"

    #: The template used to render this view.
    template_name = "django_cradmin/roleselect.django.html"

    #: The title of the page. See :meth:`.get_pagetitle`.
    pagetitle = _("What would you like to edit?")

    #: Redirect if we have a single role? See :meth:`.get_autoredirect_if_single_role`.
    autoredirect_if_single_role = True

    def get_queryset(self):
        return self.request.cradmin_instance.get_rolequeryset()

    def get(self, *args, **kwargs):
        rolecount = self.get_queryset().count()
        if rolecount == 0:
            return self.get_no_roles_response(*args, **kwargs)
        elif rolecount == 1:
            return self.get_single_role_response(*args, **kwargs)
        else:
            return self.get_multiple_roles_response(*args, **kwargs)

    def get_autoredirect_if_single_role(self):
        """
        Enables/disables automatic redirect if single role.

        Returns the value of :obj:`.autoredirect_if_single_role` by default.

        Used by :meth:`.get_single_role_response`.
        """
        return self.autoredirect_if_single_role

    def get_no_roles_response(self, *args, **kwargs):
        """
        Get the response to return if the requesting user only have no roles.

        Raises :exc:`django.core.exceptions.PermissionDenied` by default.

        If you want to do something more eloborate, you can do one of the following:

        - Use a HttpResonseRedirect to redirect to some other view/url.
        - Call ``return self.get_multiple_roles_response(*args, **kwargs)``.
          The template for this view (``django_cradmin/roleselect.django.html``) has a
          ``no_roles_section`` block. You can extend this template and
          override this block to display a custom message. You must, of course,
          set this new template as the :obj:`~.RoleSelectView.template_name`.
        """
        raise PermissionDenied()

    def get_single_role_response(self, *args, **kwargs):
        """
        Get the response to return if the requesting user only have one role.

        If :meth:`.get_autoredirect_if_single_role` returns ``True``,
        we redirect to the rolefrontpage for the role. Otherwise,
        we return :meth:`.get_multiple_roles_response`.
        """
        if self.get_autoredirect_if_single_role():
            only_role = self.get_queryset().first()
            return HttpResponseRedirect(
                self.request.cradmin_instance.rolefrontpage_url(self.request.cradmin_instance.get_roleid(only_role))
            )
        else:
            return super(RoleSelectView, self).get(*args, **kwargs)

    def get_multiple_roles_response(self, *args, **kwargs):
        """
        Get the response to return if the requesting user only has multiple roles.

        Just calls the ``get()``-method of the superclass by default.
        """
        return super(RoleSelectView, self).get(*args, **kwargs)

    def get_pagetitle(self):
        """
        Get the page title.

        Returns the value of :obj:`.pagetitle` by default.
        """
        return self.pagetitle

    def get_context_data(self, **kwargs):
        context = super(RoleSelectView, self).get_context_data(**kwargs)
        context["pagetitle"] = self.get_pagetitle()
        context["rolecount"] = self.get_queryset().count()
        self.add_javascriptregistry_component_ids_to_context(context=context)
        return context
