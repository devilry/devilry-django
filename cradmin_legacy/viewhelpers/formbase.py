from crispy_forms import layout
from django.conf import settings
from django.utils.translation import gettext_lazy
from django.views.generic import FormView as DjangoFormView

from cradmin_legacy import crapp
from cradmin_legacy.crispylayouts import CradminFormHelper


class PreviewMixin:
    """
    Mixin class to provide a preview view for your views.

    You must override :meth:`.serialize_preview`, :meth:`.deserialize_preview` and :meth:`.get_preview_url`,
    and you must call :meth:`.store_preview_in_session` before opening the preview.

    You must also ensure your template extends ``cradmin_legacy/viewhelpers/formview_base.django.html``.

    Preview data is added to a Django session using :meth:`.store_preview_in_session`,
    and popped (fetched and removed) from the session in the preview view using
    :meth:`get_preview_data`. A typical place to call :meth:`.store_preview_in_session`
    is in the form_valid() method of form views. Example::

        class MyFormView(formbase.PreviewMixin, formbase.FormView):

            # Ensure this extends cradmin_legacy/viewhelpers/formview_base.django.html
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
                    PrimarySubmit('save', gettext_lazy('Save')),

                    # When this button is clicked, self.preview_requested() returns True (see form_valid above).
                    DefaultSubmit(self.submit_preview_name, gettext_lazy('Preview'))
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
        sessionkey = f"cradmin_legacy__{cls.__module__}.{cls.__name__}"
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

    def add_context_data(self, context):
        if context.get("show_preview", False):
            context["preview_url"] = self.get_preview_url()
            context["show_preview"] = True


class FormViewMixin(PreviewMixin):
    """
    Mixin class for form views.

    See :class:`.FormView` for a ready to use view that uses this mixin,
    and see :class:`.PreviewMixin` (the superclass of this class) for docs
    on how to add previews.
    """

    #: Get the view name for the listing page.
    #: You can set this, or implement :meth:`.get_listing_url`.
    #: Defaults to :obj:`cradmin_legacy.crapp.INDEXVIEW_NAME`.
    listing_viewname = crapp.INDEXVIEW_NAME

    #: Used to add custom attributes like angularjs directives to the form.
    #: See :meth:`.get_form_attributes`.
    form_attributes = {}

    #: A list of extra form css classes. See :meth:`.get_extra_form_css_classes`.
    extra_form_css_classes = []

    #: The ID to set on the DOM element for the form. See :meth:`.get_form_id`.
    form_id = None

    #: Enable support for modelchoicefield?
    #: If this is ``False``, you will not be able to use
    #: :class:`cradmin_legacy.widgets.modelchoice.ModelChoiceWidget`
    #: in the form.
    enable_modelchoicefield_support = False

    #: Set this to True to hide the page header. See :meth:`~.FormViewMixin.get_hide_page_header`.
    hide_page_header = False

    #: The save submit label. See :meth:`~.FormViewMixin.get_submit_save_label`.
    submit_save_label = gettext_lazy("Save")

    #: The save submit label. See :meth:`~.FormViewMixin.get_submit_save_and_continue_edititing_label`.
    submit_save_and_continue_edititing_label = gettext_lazy("Save and continue editing")

    #: See :meth:`~.FormViewMixin.get_submit_save_button_name`.
    submit_save_button_name = "submit-save"

    #: See :meth:`~.FormViewMixin.get_submit_save_and_continue_edititing_button_name`.
    submit_save_and_continue_edititing_button_name = "submit-save-and-continue-editing"

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

    def get_submit_save_label(self):
        """
        Get the save submit label. Not used by this mixin, but you
        can use this in your own ``get_buttons``-method.

        Defaults to :obj:`~.FormViewMixin.submit_save_label`.
        """
        return self.submit_save_label

    def get_submit_save_and_continue_edititing_label(self):
        """
        Get the "save and continue editing" submit label. Not used by this mixin, but you
        can use this in your own ``get_buttons``-method.

        Defaults to :obj:`~.FormViewMixin.submit_save_and_continue_edititing_label`.
        """
        return self.submit_save_and_continue_edititing_label

    def get_submit_save_button_name(self):
        """
        Get the name of the save submit button. Not used by this mixin, but you
        can use this in your own ``get_buttons``-method.

        Defaults to :obj:`~.FormViewMixin.submit_save_button_name`.
        """
        return self.submit_save_button_name

    def get_submit_save_and_continue_edititing_button_name(self):
        """
        Get the "save and continue editing" submit button name.
        Not used by this mixin, but you can use this in your own ``get_buttons``-method.

        Defaults to :obj:`~.FormViewMixin.submit_save_and_continue_edititing_button_name`.
        """
        return self.submit_save_and_continue_edititing_button_name

    def get_hide_page_header(self):
        """
        Return ``True`` if we should hide the page header.

        You can override this, or set :obj:`.hide_page_header`, or hide the page header
        in all form views with the ``CRADMIN_LEGACY_HIDE_PAGEHEADER_IN_FORMVIEWS`` setting.
        """
        return self.hide_page_header or getattr(settings, "CRADMIN_LEGACY_HIDE_PAGEHEADER_IN_FORMVIEWS", False)

    def get_field_layout(self):
        """
        Get a list/tuple of fields. These are added to a ``crispy_forms.layout.Layout``.

        Must be overridden.

        Simple example::

            from django.views.generic import FormView
            from crispy_forms import layout

            class MyFormView(FormViewMixin, FormView):
                def get_field_layout(self):
                    return [
                        layout.Div(
                            'title', 'name', 'size', 'tags',
                            css_class='cradmin-globalfields')
                    ]


        A slightly more complex example::

            from crispy_forms import layout

            class MyFormView(FormViewMixin, FormView):
                def get_field_layout(self):
                    return [
                        layout.Div('title', css_class="cradmin-focusfield cradmin-focusfield-lg"),
                        layout.Div('description', css_class="cradmin-focusfield"),
                        layout.Fieldset('Metadata',
                            'size',
                            'tags'
                        )

                    ]

        """
        raise NotImplementedError()

    def get_hidden_fields(self):
        """
        Get hidden fields for the form.

        Returns:
            An iterable of :class:`crispy_forms.layout.Hidden` objects.
            Defaults to an empty list.
        """
        return []

    def get_buttons(self):
        """
        Get buttons for the form, normally one or more submit button.

        Each button must be a crispy form layout object, typically some
        subclass of :class:`crispy_forms.layout.Submit`.

        See:
            This method is used by :meth:`.get_button_layout`.
        """
        return []

    def get_button_layout(self):
        """
        Get the button layout. This is added to the crispy form layout.

        Defaults to a :class:`crispy_forms.layout.Div` with css class
        ``cradmin_legacy_submitrow`` containing all the buttons
        returned by :meth:`.get_buttons`.
        """
        return [layout.Div(*self.get_buttons(), css_class="cradmin_legacy_submitrow")]

    def get_form_attributes(self):
        """
        You can add custom attributes to the form via this method.

        This is set as the ``attrs``-attribute of the crispy FormHelper
        created in :meth:`.get_formhelper`.

        Defaults to :obj:`.form_attributes`.

        Returns:
            A dictionary to set any kind of form attributes. Underscores in
            keys are translated into hyphens.
        """
        return self.form_attributes

    def get_form_css_classes(self):
        """
        Returns list of css classes set on the form. You normally
        want to override :meth:`.get_extra_form_css_classes` instead
        of this method unless you want to provide completely custom
        form styles.
        """
        form_css_classes = ["cradmin-legacy-form"]
        form_css_classes.extend(self.get_extra_form_css_classes())
        return form_css_classes

    def get_extra_form_css_classes(self):
        """
        Returns list of extra form css classes. These classes are added to
        the default list of css classes in :meth:`.get_form_css_classes`.

        Defaults to :obj:`.extra_form_css_classes`.
        """
        return self.extra_form_css_classes

    def get_form_id(self):
        """
        Returns the ID to set on the DOM element for the form.

        Defaults to :obj:`.form_id`.
        """
        return self.form_id

    def get_formhelper_class(self):
        return CradminFormHelper

    def get_formhelper(self):
        """
        Get a :class:`crispy_forms.helper.FormHelper`.

        You normally do not need to override this directly. Instead
        you should override:

        - :meth:`.get_field_layout`.
        - :meth:`.get_hidden_fields`
        - :meth:`.get_buttons` (or perhaps :meth:`.get_button_layout`)
        """
        helper = self.get_formhelper_class()()
        helper.form_class = " ".join(self.get_form_css_classes())
        layoutargs = list(self.get_field_layout()) + list(self.get_button_layout()) + list(self.get_hidden_fields())
        helper.layout = layout.Layout(*layoutargs)
        helper.form_action = self.request.get_full_path()
        form_id = self.get_form_id()
        if form_id:
            helper.form_id = form_id

        helper.attrs = self.get_form_attributes()
        return helper

    def add_context_data(self, context):
        """
        Used by :meth:`.get_context_data` to add the context data required to
        render the form view.

        You will usually only use this when you create a view that inherits
        ``get_context_data()`` from two different superclasses (I.E.: A list view
        that also contains a form). In that case, you can use something like::

            def get_context_data(self, **kwargs):
                context = super(MyView, self).get_context_data(**kwargs)
                self.add_context_data(context)
                return context

        to add the context data required for the form.
        """
        super().add_context_data(context)
        context["formhelper"] = self.get_formhelper()
        context["enable_modelchoicefield_support"] = self.enable_modelchoicefield_support
        context["hide_pageheader"] = self.get_hide_page_header()
        context["pagetitle"] = self.get_pagetitle()
        context["pageheading"] = self.get_pageheading()

    def get_context_data(self, **kwargs):
        """
        Get the context data required to render the form view.
        """
        context = super().get_context_data(**kwargs)
        self.add_context_data(context)
        return context

    def get_listing_url(self):
        """
        Get the URL of the listing view.

        Defaults to :obj:`.listing_viewname`. This is used as the success URL
        by default.
        """
        return self.request.cradmin_app.reverse_appurl(self.listing_viewname)

    def get_default_save_success_url(self):
        if "success_url" in self.request.GET:
            return self.request.GET["success_url"]
        else:
            return self.get_listing_url()

    def get_success_url(self):
        return str(self.get_default_save_success_url())


class FormView(FormViewMixin, DjangoFormView):
    """
    A :class:`django.views.generic.edit.FormView` with :class:`.FormViewMixin`.

    Examples:

        Minimalistic example::

            from django import forms
            from django.http import HttpResponseRedirect
            from cradmin_legacy.crispylayouts import PrimarySubmit

            class MyForm(forms.Form):
                first_name = forms.CharField(max_length=50)
                last_name = forms.CharField(max_length=50)

            class MyFormView(FormView):
                template_name = 'myapp/myview.django.html'
                form_class = MyForm

                def get_field_layout(self):
                    return [
                        'first_name',
                        'last_name',
                    ]

                def get_buttons(self):
                    return [
                        PrimarySubmit('save', gettext_lazy('Save')),
                    ]

                def form_valid(self, form):
                    # ... do something with the form ...
                    return HttpResponseRedirect('/some/view')
    """

    template_name = "cradmin_legacy/viewhelpers/formview_base.django.html"
