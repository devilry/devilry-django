from django import forms
from django import http
from django.contrib import messages
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core import serializers

from . import formviewmixin
from . import previewmixin


class CreateUpdateViewMixin(previewmixin.PreviewMixin, formviewmixin.FormViewMixin):
    """
    Mixin class for Update and Create views.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.formview.CreateUpdateViewMixin``.
    """

    #: The model class.
    model = None

    #: List of field names.
    #: See :meth:`.get_model_fields` and :meth:`.get_field_layout`.
    fields = None

    #: The field that should always be set to the current role.
    #: Removes the field from the form (see :meth:`.get_form`),
    #: and instead sets the value directly on the object in
    #: :meth:`.save_object`.
    roleid_field = None

    def get_model_class(self):
        """
        Get the model class.

        Defaults to :obj:`~.CreateUpdateViewMixin.model`.
        """
        return self.model

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

    def get_form(self, form_class=None):
        """
        If you set :obj:`.roleid_field`, we will remove that field from
        the form.

        .. note::
            The :obj:`.roleid_field` handling also works for GenericForeignKey
            fields (removes the content type and object pk field from the form).
        """
        form = super(CreateUpdateViewMixin, self).get_form(form_class)
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

    @property
    def model_verbose_name(self):
        """
        Get the verbose name of the model.
        """
        return self.get_model_class()._meta.verbose_name

    def add_create_update_view_mixin_context_data(self, context):
        """
        Must be called in :meth:`.get_context_data` in subclasses
        to add the required context data.

        Args:
            context: The template context data.
        """
        self.add_preview_mixin_context_data(context=context)
        self.add_formview_mixin_context_data(context=context)
        context["model_verbose_name"] = self.model_verbose_name

    def set_automatic_attributes(self, obj, form):
        """
        Called by :meth:`.save_object` to set automatic attributes for the
        object before it is saved.

        This is where we handle :obj:`.roleid_field`, but you can override this
        to set your own automatic attributes. Just remember to call ``super``
        if you want to keep the :obj:`.roleid_field` magic.

        Parameters:
            obj: The object you are about to save.
            form: The cleaned form.
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
        self.set_automatic_attributes(obj, form)
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

    def get_success_message(self, obj):
        """
        Override this to provide a success message.

        The ``obj`` is the saved object.

        Used by :meth:`.add_success_messages`.
        """
        return None

    def add_success_messages(self, obj):
        """
        Called after the form has been saved, and after :meth:`.form_saved` has been called.

        The ``obj`` is the saved obj.

        Defaults to add :meth:`.get_success_message` as a django messages
        success message if :meth:`.get_success_message` returns anything.

        You can override this to add multiple messages or to show messages in some other way.
        """
        success_message = self.get_success_message(obj)
        if success_message:
            messages.success(self.request, success_message)

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
        :class:`django_cradmin.viewhelpers.formbase.PreviewMixin`,
        we use the model class module and name as the session key.
        This is simply because we do not want it to matter if
        you fetch preview data from create or update views
        for the same model (to simplify implementing preview views).
        """
        sessionkey = "django_cradmin__{module}.{classname}".format(
            module=cls.model.__module__, classname=cls.model.__name__
        )
        return sessionkey
