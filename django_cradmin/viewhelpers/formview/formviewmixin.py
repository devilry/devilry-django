from django_cradmin import crapp


class FormViewMixin:
    """
    Mixin class for form views.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.formview.FormViewMixin``.
    """

    #: Get the view name for the listing page.
    #: You can set this, or implement :meth:`.get_listing_url`.
    #: Defaults to :obj:`django_cradmin.crapp.INDEXVIEW_NAME`.
    listing_viewname = crapp.INDEXVIEW_NAME

    def get_pagetitle(self):
        """
        Get the page title (the title tag).
        """
        return ""

    def get_pageheading(self):
        """
        Get the page heading.

        Defaults to :meth:`.get_pagetitle`.
        """
        return self.get_pagetitle()

    def get_form_renderable(self):
        """
        Get a :class:`django_cradmin.renderable.AbstractRenderable` that renders
        the form.

        This will typically be a :doc:`uicontainer` tree containing a
        :class:`django_cradmin.uicontainer.form.Form`, but it can be any
        AbstractRenderable. Not using a :class:`django_cradmin.uicontainer.form.Form`
        (or a subclass of it) is fairly complex when it comes to handling error
        messages and form rendering, so it is generally not recommended.

        See :meth:`django_cradmin.viewhelpers.formview.formview.WithinRoleFormView` for examples.

        Returns:
            django_cradmin.renderable.AbstractRenderable: The renderable object.
        """
        raise NotImplementedError()

    def add_formview_mixin_context_data(self, context):
        """
        Must be used by get_context_data() in subclasses to add the context data required to
        render the view.

        Examples:

            Adding the required context data::

                def get_context_data(self, **kwargs):
                    context = super(MyView, self).get_context_data(**kwargs)
                    self.add_formview_mixin_context_data(context=context)
                    return context
        """
        context["form_renderable"] = self.get_form_renderable()
        context["pagetitle"] = self.get_pagetitle()
        context["pageheading"] = self.get_pageheading()

    def get_listing_url(self):
        """
        Get the URL of the listing view.

        Defaults to :obj:`.listing_viewname`. This is used as the success URL
        by default.
        """
        return self.request.cradmin_app.reverse_appurl(self.listing_viewname)

    def get_default_save_success_url(self):
        """
        Get the save success URL.

        Defaults to :meth:`.get_listing_url`, but if ``success_url`` is in
        ``request.GET``, that is used instead.
        """
        if "success_url" in self.request.GET:
            return self.request.GET["success_url"]
        else:
            return self.get_listing_url()

    def get_success_url(self):
        """
        Defaults to :meth:`.get_default_save_success_url`.
        """
        return self.get_default_save_success_url()
