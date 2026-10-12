from django.utils.translation import gettext_lazy
from django import forms
from django.views.generic import TemplateView
from django.views.generic.edit import FormMixin
from django.shortcuts import render
from django import http
from crispy_forms import layout

from cradmin_legacy import crapp
from cradmin_legacy.crispylayouts import CradminFormHelper


class MultiSelectView(TemplateView):
    """
    Base view for multiselect views (views used when the
    user selects one or more items for some action).

    You must override:
    - :meth:`.get_queryset_for_role`.
    - :meth:`.object_selection_valid`
    """

    #: The view name for the success page.
    #: You can set this, or implement :meth:`.get_listing_url`.
    #: Defaults to :obj:`cradmin_legacy.crapp.INDEXVIEW_NAME`.
    success_viewname = crapp.INDEXVIEW_NAME

    def get_queryset_for_role(self, role):
        """
        Get a queryset with all objects of ``self.model``  that
        the current role can access.
        """
        raise NotImplementedError()

    def get_queryset(self):
        """
        DO NOT override this. Override :meth:`.get_queryset_for_role`
        instead.
        """
        queryset = self.get_queryset_for_role(self.request.cradmin_role)
        return queryset

    def _get_selected_objects_form_class(self):
        class MultiSelectForm(forms.Form):
            selected_objects = forms.ModelMultipleChoiceField(
                widget=forms.MultipleHiddenInput, queryset=self.get_queryset()
            )

        return MultiSelectForm

    def _get_selected_objects_form(self):
        form_class = self._get_selected_objects_form_class()
        return form_class(data=self.request.POST)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        self.selected_objects_form = self._get_selected_objects_form()
        if self.selected_objects_form.is_valid():
            self.selected_objects = self.selected_objects_form.cleaned_data["selected_objects"]
            return self.object_selection_valid()
        else:
            return self.object_selection_invalid(self.selected_objects_form)

    def is_first_load(self):
        """
        Can be used by subclasses to check if this is the
        first/initial load of this view (right after
        the user submits the form where they selected what
        to perform the action for).
        """
        return "is_the_multiselect_form" in self.request.POST

    def object_selection_valid(self):
        """
        Called if the form used to validate the selected objects is valid.
        Must be overridden.

        The selected objects is available as ``self.selected_objects``.
        """
        raise NotImplementedError()

    def object_selection_invalid(self, form):
        """
        Called if the form used to validate the selected objects is invalid.
        Must be overridden.
        """
        return render(
            self.request,
            "cradmin_legacy/error.django.html",
            {
                "error": gettext_lazy(
                    "Invalid selection. This is usually caused by someone else changing "
                    "permissions while you where selecting items to edit."
                )
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_objects_form"] = self.selected_objects_form
        context["selected_objects"] = self.selected_objects
        return context

    def get_success_url(self):
        """
        Get the URL to redirect to on success.

        Defaults to :obj:`.success_viewname`.
        """
        return self.request.cradmin_app.reverse_appurl(self.success_viewname)

    def success_redirect_response(self):
        """
        Return a :class:`django.http.HttpResponseRedirect` response with
        :meth:`.get_success_url` as the URL.
        """
        return http.HttpResponseRedirect(self.get_success_url())


class NoFormActionFormHelper(CradminFormHelper):
    form_action = ""


class MultiSelectFormView(MultiSelectView, FormMixin):
    """
    Extends :class:`.MultiSelectView` and :class:`django.views.generic.edit.FormMixin`
    to make a base class for multiselect form views.

    You must override:
    - :meth:`.get_queryset_for_role`
    - :meth:`.form_valid`
    - :meth:`.get_field_layout`

    And you have to set:
    - :obj:`~.MultiSelectFormView.model`, or override a method as explained in its docs.
    - ``form_class`` or override ``get_form_class(...)`` as documented in the Django FormMixin docs.

    You will most likely also want to override :meth:.get_buttons`.
    """

    template_name = "cradmin_legacy/viewhelpers/multiselect/formview.django.html"

    #: The model class to edit. You do not have to specify
    #: this, but if you do not specify this, you have to override
    #: :meth:`.get_pagetitle`.
    model = None

    #: The field that should always be set to the current role.
    #: Adds a hidden field with the correct value for the current
    #: role. See :meth:`.get_hidden_fields`.
    roleid_field = None

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.

        Overridden to handle the fact that we always POST. So instead
        of distinquishing between POST and GET, we check
        :meth:`.MultiSelectView.is_first_load`.
        """
        kwargs = {
            "initial": self.get_initial(),
            "prefix": self.get_prefix(),
        }

        if not self.is_first_load() and self.request.method in ("POST", "PUT"):
            kwargs.update(
                {
                    "data": self.request.POST,
                    "files": self.request.FILES,
                }
            )
        return kwargs

    def object_selection_valid(self):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if self.is_first_load():
            return self.first_load(form)
        else:
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

    def first_load(self, form):
        """
        Called on the first load of the page (right after
        the user submits the form where they selected what
        to edit).
        """
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        """
        Called when the form is invalid.
        """
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        """
        Called when the form is valid. Must be overridden.

        You will normally want to do something with the form data
        here, and redirect to a success page.
        """
        raise NotImplementedError()

    def get_pagetitle(self):
        """
        Get the page title/heading.

        Defaults to the ``verbose_name_plural`` of the :obj:`~.MultiSelectFormView.model`.
        """
        return self.model._meta.verbose_name_plural

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pagetitle"] = self.get_pagetitle()
        context["formhelper"] = self.get_formhelper()
        return context

    def get_field_layout(self):
        """
        Get a list/tuple of fields. These are added to a ``crispy_forms.layout.Layout``.
        Defaults to a all fields on the model. If :obj:`.fields`, we use those fields.

        Simple example (same as specifying the fields in :obj:`.fields`)::

            from crispy_forms import layout

            class MyCreateView(CreateView):
                def get_field_layout(self):
                    return [
                        layout.Div(
                            'title', 'name', 'size', 'tags',
                            css_class='cradmin-globalfields')
                    ]

        A slightly more complex example::

            from crispy_forms import layout

            class MyEditView(MultiSelectFormView):
                def get_field_layout(self):
                    return [
                        layout.Div('data', css_class="cradmin-focusfield"),
                    ]

        """
        raise NotImplementedError()

    def get_hidden_fields(self):
        """
        Get hidden fields for the form.

        If you set :obj:`.roleid_field`, a hidden field named whatever you
        specify in :obj:`.roleid_field` with value set to the current role ID
        is added automatically.

        Returns:
            An iterable of :class:`crispy_forms.layout.Hidden` objects.
        """
        fields = []
        if self.roleid_field:
            roleid = self.request.cradmin_instance.get_roleid(self.request.cradmin_role)
            fields.append(layout.Hidden(self.roleid_field, roleid))
        return fields

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

    def get_formhelper(self):
        """
        Get a :class:`crispy_forms.helper.FormHelper`.

        You normally do not need to override this directly. Instead
        you should override:

        - :meth:`.get_field_layout`.
        - :meth:`.get_hidden_fields`
        - :meth:`.get_buttons` (or perhaps :meth:`.get_button_layout`)
        """
        helper = NoFormActionFormHelper()
        layoutargs = list(self.get_field_layout()) + list(self.get_button_layout()) + list(self.get_hidden_fields())
        helper.layout = layout.Layout(*layoutargs)
        helper.form_tag = False  # NOTE: We render the form tag in the template because we render multiple forms.
        helper.disable_csrf = True  # NOTE: We render csrf token in the template.
        return helper
