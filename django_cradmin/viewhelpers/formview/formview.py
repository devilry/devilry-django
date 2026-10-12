from django.views.generic import FormView as DjangoFormView
from django_cradmin import javascriptregistry
from django_cradmin.viewhelpers.mixins import CommonCradminViewMixin

from . import formviewmixin


class WithinRoleFormView(
    javascriptregistry.viewmixin.WithinRoleViewMixin,
    formviewmixin.FormViewMixin,
    CommonCradminViewMixin,
    DjangoFormView,
):
    """
    Form view with the correct context data and sane base template
    for views where we have a cradmin role.

    Uses :class:`django.views.generic.edit.FormView` with
    :class:`django_cradmin.viewhelpers.formview.formviewmixin.FormViewMixin`
    and :class:`django_cradmin.javascriptregistry.viewmixin.WithinRoleViewMixin`.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.formview.WithinRoleFormView``.

    Examples:

        Minimalistic example::

            from django import forms
            from django.http import HttpResponseRedirect
            from django_cradmin import viewhelpers

            class MyForm(forms.Form):
                first_name = forms.CharField(max_length=50)
                last_name = forms.CharField(max_length=50)

            class MyFormView(viewhelpers.formview.WithinRoleFormView):
                template_name = 'myapp/myview.django.html'
                form_class = MyForm

                def get_form_renderable(self):
                    return uicontainer.layout.AdminuiPageSectionTight(
                        children=[
                            uicontainer.form.Form(
                                form=self.get_form(),
                                children=[
                                    uicontainer.fieldwrapper.FieldWrapper(
                                        fieldname='first_name',
                                        # Override field renderable to set autofocus
                                        field_renderable=uicontainer.field.Field(autofocus=True)
                                    ),
                                    uicontainer.fieldwrapper.FieldWrapper('last_name'),
                                    uicontainer.button.SubmitPrimary(text='Save')
                                ]
                            )
                        ]
                    ).bootstrap()

                def form_valid(self, form):
                    # ... do something with the form ...
                    return HttpResponseRedirect('/some/view')
    """

    template_name = "django_cradmin/viewhelpers/formview/within_role_form_view.django.html"

    def get_context_data(self, **kwargs):
        context = super(WithinRoleFormView, self).get_context_data(**kwargs)
        self.add_formview_mixin_context_data(context=context)
        self.add_javascriptregistry_component_ids_to_context(context=context)
        self.add_common_view_mixin_data_to_context(context=context)
        return context


class StandaloneFormView(
    javascriptregistry.viewmixin.StandaloneBaseViewMixin,
    formviewmixin.FormViewMixin,
    CommonCradminViewMixin,
    DjangoFormView,
):
    """
    Form view with the correct context data and sane base template
    for views where we do not have a cradmin role.

    .. note:: You should import this class with ``from django_cradmin import viewhelpers``,
        and refer to it using ``viewhelpers.formview.StandaloneFormView``.
    """

    template_name = "django_cradmin/viewhelpers/formview/standalone_form_view.django.html"

    def get_context_data(self, **kwargs):
        context = super(StandaloneFormView, self).get_context_data(**kwargs)
        self.add_formview_mixin_context_data(context=context)
        self.add_javascriptregistry_component_ids_to_context(context=context)
        self.add_common_view_mixin_data_to_context(context=context)
        return context
