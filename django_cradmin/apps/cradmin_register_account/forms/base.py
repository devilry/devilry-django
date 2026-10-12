from builtins import object

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from django_cradmin import uicontainer


class AbstractCreateAccountForm(forms.ModelForm):
    """
    Base class for account creation forms.

    Subclasses **must** override:

    - :meth:`~.AbstractCreateAccountForm.set_password`.
    - :meth:`~.AbstractCreateAccountForm.get_field_renderables`.
    """

    class Meta(object):
        model = get_user_model()
        fields = []

    def get_submit_button_label(self):
        """
        Returns the submit button label.

        Override this to provide a custom label.
        """
        return _("Sign up for %(sitename)s") % {"sitename": settings.DJANGO_CRADMIN_SITENAME}

    def set_password(self, user):
        """
        Set the password of the given ``user``.

        **Must** be overridden in subclasses.

        Should not save the user, only set the password.

        Typically this will retrieve the password from the form, or
        generate a password, and set the password using ``user.set_password``. Example::

            class MyCreateAccountForm(AbstractCreateAccountForm):
                ...
                def set_password(self, user):
                    raw_password = 'secret'  # or self.cleaned_data['password']
                    user.set_password(raw_password)

        """
        raise NotImplementedError()

    def set_extra_user_attributes(self, user):
        """
        Override this to set extra user attributes in addition to
        :meth:`~.AbstractCreateAccountForm.deactivate_user` and
        :meth:`~.AbstractCreateAccountForm.set_password`.
        """

    def set_extra_user_attributes_before_clean(self, user):
        """
        Override this to set extra user attributes before the any cleaning is run on the user instance.
        """

    def get_field_renderables(self):
        """
        Get field renderables.

        Must be overridden in subclasses.

        Returns:
            list: List of :class:`django_cradmin.uicontainer.container.AbstractContainerRenderable`.
        """
        raise NotImplementedError()

    def get_submit_button_renderables(self):
        return [uicontainer.button.SubmitPrimary(text=self.get_submit_button_label())]

    def get_form_renderable(self):
        """
        Get a :class:`django_cradmin.renderable.AbstractRenderable` that renders
        the form.

        This will typically be a :doc:`uicontainer` tree containing a
        :class:`django_cradmin.uicontainer.form.Form`, but it can be any
        AbstractRenderable. Not using a :class:`django_cradmin.uicontainer.form.Form`
        (or a subclass of it) is fairly complex when it comes to handling error
        messages and form rendering, so it is generally not recommended.

        Returns:
            django_cradmin.renderable.AbstractRenderable: The renderable object.
        """
        return uicontainer.form.Form(
            form=self,
            children=[
                uicontainer.layout.AdminuiPageSectionTight(
                    children=self.get_field_renderables() + self.get_submit_button_renderables()
                )
            ],
        ).bootstrap()

    def save(self, commit=True):
        user = super(AbstractCreateAccountForm, self).save(commit=False)
        self.set_password(user)
        self.set_extra_user_attributes(user)
        user.full_clean()
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_extra_user_attributes_before_clean(user=self.instance)


class AbstractCreateAccountWithPasswordForm(AbstractCreateAccountForm):
    """
    Extends :class:`.AbstractCreateAccountForm` with the typical
    password + repeat password fields. Validates that the passwords
    match.

    Subclasses **must** override:

    - :meth:`~.AbstractCreateAccountForm.deactivate_user`.
    """

    #: The first password.
    password1 = forms.CharField(label=_("Type your password"), widget=forms.PasswordInput)

    #: The repeat password fields.
    password2 = forms.CharField(label=_("Type your password one more time"), widget=forms.PasswordInput)

    def set_password(self, user):
        """
        Set the password of the user using ``user.set_password(...)``.

        Does not save the user.
        """
        raw_password = self.cleaned_data["password1"]
        user.set_password(raw_password)

    def clean(self):
        """
        Validate the form.

        The default implementation validates that the passwords
        match.

        Make sure to call super if you override this::

            class MyCreateAccountForm(AbstractCreateAccountWithPasswordForm):
                ...
                def clean(self):
                    cleaned_data = super(MyCreateAccountForm, self).clean()
                    # ...
                    return cleaned_data
        """
        cleaned_data = super(AbstractCreateAccountWithPasswordForm, self).clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(message=_("The passwords do not match."), code="passwords_do_not_match")
        return cleaned_data
