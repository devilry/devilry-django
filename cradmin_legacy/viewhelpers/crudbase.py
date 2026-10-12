import urllib.parse

from crispy_forms import layout
from django import forms, http
from django.contrib import messages
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core import serializers
from django.utils.translation import gettext_lazy

from cradmin_legacy import automodelform
from cradmin_legacy.crispylayouts import DefaultSubmit, PrimarySubmit

from . import formbase


class CreateUpdateViewMixin(formbase.FormViewMixin):
    """
    Mixin class for Update and Create views.
    """

    #: The model class.
    model = None

    #: List of field names.
    #: See :meth:`.get_model_fields` and :meth:`.get_field_layout`.
    fields = None

    #: The name of the submit button used for preview.
    #: Only used when :meth:`.preview_url` is defined.
    submit_preview_name = "submit-preview"

    #: The field that should always be set to the current role.
    #: Removes the field from the form (see :meth:`.get_form`),
    #: and instead sets the value directly on the object in
    #: :meth:`.save_object`.
    roleid_field = None

    #: The viewname within this app for the edit view.
    #: See :meth:`.get_editurl`.
    editview_appurl_name = "edit"

    def get_model_class(self):
        """
        Get the model class.

        Defaults to :obj:`~.CreateUpdateViewMixin.model`.
        """
        return self.model

    def make_default_form_class(self):
        """
        Make a ModelForm class with the model set to
        :meth:`.get_model_class` and the fields set to
        :meth:`.get_model_fields`.
        """
        me = self

        class Form(automodelform.ModelForm):
            class Meta:
                model = me.get_model_class()
                fields = me.get_model_fields()

        return Form

    def get_form_class(self):
        if self.form_class:
            return self.form_class
        else:
            return self.make_default_form_class()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        form_class = self.get_form_class()
        if issubclass(form_class, automodelform.ModelForm):
            kwargs["view"] = self
        return kwargs

    def add_preview_button_if_configured(self, buttons):
        preview_url = self.get_preview_url()
        if preview_url:
            buttons.append(DefaultSubmit(self.submit_preview_name, gettext_lazy("Preview")))

    def get_model_fields(self):
        """
        Get model fields. Defaults to :obj:`.fields`.
        """
        if self.fields:
            return self.fields
        else:
            fields = list(forms.fields_for_model(self.get_model_class(), fields=self.fields).keys())
            if self.roleid_field and self.roleid_field in fields:
                fields.remove(self.roleid_field)
            return fields

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

            class MyCreateView(CreateView):
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
        fields = self.get_model_fields()
        return [layout.Div(*fields, css_class="cradmin-globalfields")]

    def get_form(self, form_class=None):
        """
        If you set :obj:`.roleid_field`, we will remove that field from
        the form.

        .. note::
            The :obj:`.roleid_field` handling also works for GenericForeignKey
            fields (removes the content type and object pk field from the form).
        """
        form = super().get_form(form_class)
        if self.roleid_field:
            roleid_fieldobject = getattr(self.get_model_class(), self.roleid_field, None)
            if isinstance(roleid_fieldobject, GenericForeignKey):
                for fieldname in roleid_fieldobject.fk_field, roleid_fieldobject.ct_field:
                    if fieldname in form.fields:
                        del form.fields[fieldname]
            else:
                if self.roleid_field in form.fields:
                    del form.fields[self.roleid_field]
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["model_verbose_name"] = self.get_model_class()._meta.verbose_name
        return context

    def get_editurl(self, obj):
        """
        Get the edit URL for ``obj``.

        Defaults to::

            self.request.cradmin_app.reverse_appurl(self.editview_appurl_name, args=[obj.pk])
        """
        return self.request.cradmin_app.reverse_appurl(self.editview_appurl_name, args=[obj.pk])

    def _get_full_editurl(self, obj):
        url = self.get_editurl(obj)
        if "success_url" in self.request.GET:
            url = "{}?{}".format(url, urllib.parse.urlencode({"success_url": self.request.GET["success_url"]}))
        return url

    def get_success_url(self):
        if self.get_submit_save_and_continue_edititing_button_name() in self.request.POST:
            return str(self._get_full_editurl(self.object))
        else:
            return str(self.get_default_save_success_url())

    def set_automatic_attributes(self, obj):
        """
        Called by :meth:`.save_object` to set automatic attributes for the
        object before it is saved.

        This is where we handle :obj:`.roleid_field`, but you can override this
        to set your own automatic attributes. Just remember to call ``super``
        if you want to keep the :obj:`.roleid_field` magic.

        Parameters:
            obj: The object you are about to save.
        """
        if self.roleid_field:
            setattr(obj, self.roleid_field, self.request.cradmin_role)

    def save_object(self, form, commit=True):
        """
        Save the object. You can override this to customize how the
        form is turned into a saved object.

        Make sure you call ``super`` if you override this (see the docs for the commit parameter).
        If you do not, you will loose the automatic handling of obj:`.roleid_field`.

        Parameters:
            commit (boolean): If this is ``False``, the object is returned
                unsaved. Very useful when you want to manipulate the object
                before saving it in a subclass.

        Returns:
            The saved object.
        """
        obj = form.save(commit=False)
        self.set_automatic_attributes(obj=obj)
        if commit:
            obj = form.save(commit=True)
        return obj

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        if self.preview_requested():
            self.store_preview_in_session(self.serialize_preview(form))
            return self.render_to_response(self.get_context_data(form=form, show_preview=True))
        else:
            self.object = self.save_object(form)
            self.form_saved(self.object)
            self.add_success_messages(self.object)
            return http.HttpResponseRedirect(self.get_success_url())

    def form_saved(self, object):
        """
        Called after the form has been successfully saved.
        The ``object`` is the saved object.

        Does nothing by default, but you can override it if you need to
        do something extra post save.
        """
        pass

    def get_success_message(self, object):
        """
        Override this to provide a success message.

        The ``object`` is the saved object.

        Used by :meth:`.add_success_messages`.
        """
        return None

    def add_success_messages(self, object):
        """
        Called after the form has been saved, and after :meth:`.form_saved` has been called.

        The ``object`` is the saved object.

        Defaults to add :meth:`.get_success_message` as a django messages
        success message if :meth:`.get_success_message` returns anything.

        You can override this to add multiple messages or to show messages in some other way.
        """
        success_message = self.get_success_message(object)
        if success_message:
            messages.success(self.request, success_message)

    def get_form_invalid_message(self, form):
        """
        You can override this to provide a custom error message.

        Defaults to "Please fix the errors in the form below.".

        The ``form`` is the invalid form object.

        Used by :meth:`.add_form_invalid_messages`.
        """
        return gettext_lazy("Please fix the errors in the form below.")

    def add_form_invalid_messages(self, form):
        """
        Called to add messages when the form does not validate.

        The ``form`` is the invalid form object.

        Defaults to add :meth:`.get_form_invalid_message` as a django messages
        error message if :meth:`.get_form_invalid_message` returns anything.

        You can override this to add multiple messages or to show error messages in some other way.
        """
        form_invalid_message = self.get_form_invalid_message(object)
        if form_invalid_message:
            messages.error(self.request, form_invalid_message)

    def form_invalid(self, form):
        self.add_form_invalid_messages(form)
        return super().form_invalid(form)

    def serialize_preview(self, form):
        """
        Seralize for preview.

        Defaults to serializing the object as JSON using ``django.core.serializers``.
        You can safely override this, but you will also have to override
        :meth:`deserialize_preview`.
        """
        return serializers.serialize("json", [self.save_object(form, commit=False)])

    @classmethod
    def deserialize_preview(cls, serialized):
        """
        Deseralize a preview serialized with :meth:`.serialize_preview`.

        You must override this and :meth:`.serialize_preview` - they work together
        to send the preview to the preview View.
        """
        return list(serializers.deserialize("json", serialized))[0].object

    @classmethod
    def get_preview_sessionkey(cls):
        """
        Get the session key used for preview. You should not
        need to override this.

        Unlike the default implementation of this method from
        :class:`cradmin_legacy.viewhelpers.formbase.PreviewMixin`,
        we use the model class module and name as the session key.
        This is simply because we do not want it to matter if
        you fetch preview data from create or update views
        for the same model (to simplify implementing preview views).
        """
        sessionkey = "cradmin_legacy__{module}.{classname}".format(
            module=cls.model.__module__, classname=cls.model.__name__
        )
        return sessionkey


class OnlySaveButtonMixin:
    """
    Mixin class that overrides ``get_buttons()`` to just include
    the save button (no "Save and continue editing").

    You must mix this in **before** any :class:`.CreateUpdateViewMixin`
    subclass (like UpdateView or CreateView).
    """

    def get_buttons(self):
        if hasattr(self, "is_in_foreignkey_select_mode") and self.is_in_foreignkey_select_mode():
            return super().get_buttons()
        buttons = [
            PrimarySubmit(self.get_submit_save_button_name(), self.get_submit_save_label()),
        ]
        self.add_preview_button_if_configured(buttons)
        return buttons
