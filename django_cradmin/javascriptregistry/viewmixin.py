from django_cradmin.javascriptregistry.default_componentids import get_default_component_ids


class MinimalViewMixin(object):
    """
    Views that use the javascriptregistry template tags must
    use this mixin. The base templates for cradmin uses these template
    tags, so this means that this mixin is essential for most views.
    You will normally want to mix in one of the subclasses:

    - :class:`.StandaloneBaseViewMixin`
    - :class:`.WithinRoleViewMixin`

    Or extend one of the views in ``django_cradmin.viewhelpers``.

    Examples:

        Usage (same for the subclasses)::

            class MyView(TemplateView, javascriptregistry.viewmixin.MinimalViewMixin):
                def get_context_data(self, **kwargs):
                    context = super(MinimalViewMixin, self).get_context_data(**kwargs)
                    self.add_javascriptregistry_component_ids_to_context(context=context)
                    return context
    """

    def get_javascriptregistry_component_ids(self):
        return get_default_component_ids()

    def add_javascriptregistry_component_ids_to_context(self, context):
        """
        Call this to add the ``cradmin_javascriptregistry_component_ids`` template
        context variable to the provided ``context``.

        Do not override this in subclasses.

        Args:
            context (dict): A template context.

        """
        context["cradmin_javascriptregistry_component_ids"] = self.get_javascriptregistry_component_ids()


class StandaloneBaseViewMixin(MinimalViewMixin):
    """
    Use with views that use the ``django_cradmin/standalone-base.django.html``
    template.

    DO NOT use for views that use the ``django_cradmin/base.django.html`` template,
    use :class:`.ViewMixin` for that.
    """

    def get_javascriptregistry_component_ids(self):
        if getattr(self.request, "cradmin_instance", None):
            return self.request.cradmin_instance.get_default_javascriptregistry_component_ids()
        else:
            return super(StandaloneBaseViewMixin, self).get_javascriptregistry_component_ids()


class WithinRoleViewMixin(StandaloneBaseViewMixin):
    """
    Use with views that use the ``django_cradmin/base.django.html`` template.
    """

    def get_javascriptregistry_component_ids(self):
        if getattr(self.request, "cradmin_instance", None):
            return self.request.cradmin_instance.get_default_within_role_javascriptregistry_component_ids()
        else:
            return super(WithinRoleViewMixin, self).get_javascriptregistry_component_ids()
