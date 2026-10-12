class PreviewMixin:
    """
    Mixin class to provide a preview view for your views.

    You must override :meth:`.serialize_preview`, :meth:`.deserialize_preview` and :meth:`.get_preview_url`,
    and you must call :meth:`.store_preview_in_session` before opening the preview.

    You must also ensure your template extends ``django_cradmin/viewhelpers/formview_base.django.html``.

    Preview data is added to a Django session using :meth:`.store_preview_in_session`,
    and popped (fetched and removed) from the session in the preview view using
    :meth:`get_preview_data`. A typical place to call :meth:`.store_preview_in_session`
    is in the form_valid() method of form views. Example::

        class MyFormView(viewhelpers.formview.PreviewMixin, viewhelpers.formview.WithinRoleFormView):

            # Ensure this extends django_cradmin/viewhelpers/formview_base.django.html
            template_name = 'myapp/mytemplate.django.html'


            # ... other required code for formbase.FormView ...


            def form_valid(self, form):
                if self.preview_requested():
                    self.store_preview_in_session(self.serialize_preview(form))
                    return self.render_to_response(self.get_context_data(form=form, show_preview=True))
                else:
                    # ... save, update, or whatever you do on POST when preview is not requested ...

            def get_buttons(self):
                return [
                    PrimarySubmit('save', _('Save')),

                    # When this button is clicked, self.preview_requested() returns True (see form_valid above).
                    DefaultSubmit(self.submit_preview_name, _('Preview'))
                ]

            def serialize_preview(self, form):
                return json.dumps({
                    'title': form.cleaned_data['title'],
                    'description': form.cleaned_data['description'],
                })

            @classmethod
            def deserialize_preview(cls, serialized):
                return json.loads(serialized)


    If you have something like MyFormView implemented, a preview view is as simple as this::

        class MyPreviewView(View):
            def get(request):
                preview_data = MyFormView.get_preview_data()
                return HttpResponse(...)

    How you render your preview data in your view is entirely up to you - a TemplateView
    that fetches preview data in get_context_data() is ususally more approproate than a
    View like the example above.
    """

    #: The name of the submit button used for preview.
    submit_preview_name = "submit-preview"

    def preview_requested(self):
        """
        Determine if a preview was requested.

        Defaults to checking if :obj:`.submit_preview_name` is
        in ``request.POST``.
        """
        return self.submit_preview_name in self.request.POST

    def store_preview_in_session(self, data):
        self.request.session[self.__class__.get_preview_sessionkey()] = data

    def serialize_preview(self, form):
        """
        Seralize data for preview.

        You must override this and :meth:`.deserialize_preview` - they work together
        to send the preview to the preview View. You can return anything that can
        be put into a Django session here. We recommend returning a string to
        ensure your code work with any session backend. JSON encoding is a good choice
        is most cases.
        """
        raise NotImplementedError()

    @classmethod
    def deserialize_preview(cls, serialized):
        """
        Deseralize a preview serialized with :meth:`.serialize_preview`.

        You must override this and :meth:`.serialize_preview` - they work together
        to send the preview to the preview View.
        """
        raise NotImplementedError()

    @classmethod
    def get_preview_sessionkey(cls):
        """
        Get the session key used for preview. You should not
        need to override this.
        """
        sessionkey = "django_cradmin__{module}.{classname}".format(module=cls.__module__, classname=cls.__name__)
        return sessionkey

    @classmethod
    def get_preview_data(cls, request):
        """
        Get the preview data.

        You should use this in the preview view to get the
        data for the preview.

        You normally do not override this. If you want to manage
        serialization yourself, see :meth:`.serialize_preview`.
        """
        serialized = request.session.pop(cls.get_preview_sessionkey())
        return cls.deserialize_preview(serialized)

    def get_preview_url(self):
        """
        Get the URL of the preview view.
        """
        return None

    def add_preview_mixin_context_data(self, context):
        """
        Must be used by get_context_data() in subclasses to add the context data required to
        render the view.

        Examples:

            Adding the required context data::

                def get_context_data(self, **kwargs):
                    context = super(MyView, self).get_context_data(**kwargs)
                    self.add_preview_mixin_context_data(context=context)
                    return context
        """
        if context.get("show_preview", False):
            context["preview_url"] = self.get_preview_url()
            context["show_preview"] = True
