# Python imports
from __future__ import unicode_literals

from crispy_forms import layout
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import ugettext_lazy
from django_cradmin.viewhelpers import update

from devilry.devilry_cradmin import devilry_acemarkdown
from devilry.devilry_group import models as group_models


class EditGroupCommentForm(forms.ModelForm):
    """
    Form for editing existing Feedback drafts.
    """
    hidden_initial_data = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        fields = ['text', 'hidden_initial_data']
        model = group_models.GroupComment

    @classmethod
    def get_field_layout(cls):
        return ['text']

    def clean(self):
        if 'hidden_initial_data' not in self.cleaned_data:
            raise ValidationError(message='')
        if self.cleaned_data['hidden_initial_data'] == self.cleaned_data['text']:
            raise ValidationError(message='')

    def __init__(self, **kwargs):
        super(EditGroupCommentForm, self).__init__(**kwargs)
        self.fields['hidden_initial_data'].initial = self.instance.text


class EditGroupCommentBase(update.UpdateView):
    model = group_models.GroupComment

    def dispatch(self, request, *args, **kwargs):
        if len(self.get_queryset_for_role(request.cradmin_role)) == 0:
            raise Http404()
        return super(EditGroupCommentBase, self).dispatch(request, *args, **kwargs)

    def get_queryset_for_role(self, role):
        return group_models.GroupComment.objects.filter(
                feedback_set__group=role,
                user=self.request.user,
                id=self.kwargs.get('pk'))

    def get_form_class(self):
        return EditGroupCommentForm

    def get_form(self, form_class=None):
        form = super(EditGroupCommentBase, self).get_form(form_class=form_class)
        form.fields['text'].widget = devilry_acemarkdown.Small()
        form.fields['text'].label = False
        return form

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('text', focusonme='focusonme', css_class='form-control'),
                css_class='cradmin-globalfields'
            )
        ]

    def form_invalid(self, form):
        messages.success(self.request, ugettext_lazy('No changes, comment not updated'))
        return HttpResponseRedirect(self.request.cradmin_app.reverse_appindexurl())

    def save_object(self, form, commit=False):
        comment = super(EditGroupCommentBase, self).save_object(form=form, commit=True)
        return comment

    def get_success_message(self, object):
        messages.success(self.request, ugettext_lazy('Comment updated!'))

    def get_success_url(self):
        if self.get_submit_save_and_continue_edititing_button_name() in self.request.POST:
            return self.request.cradmin_app.reverse_appurl(
                'groupcomment-edit',
                args=self.args,
                kwargs=self.kwargs)
        else:
            return self.request.cradmin_app.reverse_appindexurl()