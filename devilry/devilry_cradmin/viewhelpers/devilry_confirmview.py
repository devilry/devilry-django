from django import forms
from django_cradmin.crispylayouts import PrimarySubmit
from django_cradmin.viewhelpers import formbase


class View(formbase.FormView):
    template_name = 'devilry_cradmin/viewhelpers/devilry_confirmview.django.html'
    form_class = forms.Form

    def get_field_layout(self):
        return []

    def get_submit_button_class(self):
        return PrimarySubmit

    def get_submit_button_label(self):
        raise NotImplementedError()

    def get_button_layout(self):
        return [
            self.get_submit_button_class()('confirm',
                                           self.get_submit_button_label())
        ]

    def get_form_css_classes(self):
        return []

    def get_confirm_message(self):
        return ''

    def get_backlink_url(self):
        raise NotImplementedError()

    def get_backlink_label(self):
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        context = super(View, self).get_context_data(**kwargs)
        context['confirm_message'] = self.get_confirm_message()
        context['backlink_url'] = self.get_backlink_url()
        context['backlink_label'] = self.get_backlink_label()
        return context
