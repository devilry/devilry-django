import htmls
import mock
from django import forms
from django_cradmin import uicontainer


class SingleFormRenderableHelperMixin(object):
    def single_field_formclass_factory(self, field):
        class TestForm(forms.Form):
            testfield = field

        return TestForm

    def single_field_formrenderable_fieldwrapper_factory(self):
        return uicontainer.fieldwrapper.FieldWrapper(fieldname="testfield")

    def single_field_formrenderable_factory(self, field, formvalue=None, fieldwrapper=None):
        form_class = self.single_field_formclass_factory(field=field)
        data = None
        if formvalue:
            data = {"testfield": formvalue}
        form = form_class(data=data)
        fieldwrapper = fieldwrapper or self.single_field_formrenderable_fieldwrapper_factory()
        formrenderable = uicontainer.form.Form(form=form, children=[fieldwrapper]).bootstrap()
        return formrenderable

    def single_field_formrenderable_htmls(self, **kwargs):
        formrenderable = self.single_field_formrenderable_factory(**kwargs)
        return htmls.S(formrenderable.render(request=mock.MagicMock()))
