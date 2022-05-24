# Python imports


from crispy_forms import layout
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.utils.translation import gettext_lazy
from cradmin_legacy.viewhelpers import update

from devilry.devilry_group import models as group_models
from devilry.devilry_comment.editor_widget import DevilryMarkdownWidget


class EditGroupCommentForm(forms.ModelForm):
    """
    Form for editing existing Feedback drafts.
    """

    class Meta:
        fields = ['text']
        model = group_models.GroupComment

    @classmethod
    def get_field_layout(cls):
        return ['text']

    def clean(self):
        if self.instance.text == self.cleaned_data['text']:
            raise ValidationError(message='')


class EditGroupCommentBase(update.UpdateView):
    """
    Base class for editing :class:`.devilry.devilry_group.models.GroupComment`s.

    This view can be used standalone, without being subclassed, but usually some extra checks needs
    to be performed based on the role of the user.

    By default this requires that the user that edits the comment, is also the user
    that "owns" the comment.

    If you need to do some extra checks, subclass this class and override the appropriate methods.
    """
    template_name = 'devilry_group/group_comment_edit_base.django.html'
    model = group_models.GroupComment

    def dispatch(self, request, *args, **kwargs):
        if len(self.get_queryset_for_role(request.cradmin_role)) == 0:
            raise Http404()
        return super(EditGroupCommentBase, self).dispatch(request, *args, **kwargs)

    def get_pagetitle(self):
        return gettext_lazy('Edit comment')

    def get_pageheading(self):
        return gettext_lazy('Edit comment')

    def get_queryset_for_role(self, role):
        return group_models.GroupComment.objects.filter(
                feedback_set__group=role,
                user=self.request.user,
                id=self.kwargs.get('pk'))

    def get_form_class(self):
        return EditGroupCommentForm

    def get_form(self, form_class=None):
        form = super(EditGroupCommentBase, self).get_form(form_class=form_class)
        form.fields['text'].widget = DevilryMarkdownWidget(request=self.request)
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
        messages.success(self.request, gettext_lazy('No changes, comment not updated'))
        return HttpResponseRedirect(str(self.__get_redirect_url()))

    def save_object(self, form, commit=False):
        comment = super(EditGroupCommentBase, self).save_object(form=form, commit=True)
        return comment

    def get_success_message(self, object):
        messages.success(self.request, gettext_lazy('Comment updated!'))

    def __get_redirect_url(self):
        """
        If the `Save and continue editing` is pressed, this returns the url path to the edit view,
        else it returns the url path to the feedback feed.
        """
        if self.get_submit_save_and_continue_edititing_button_name() not in self.request.POST:
            return self.request.cradmin_app.reverse_appindexurl()
        return self.request.cradmin_app.reverse_appurl(
            'groupcomment-edit',
            args=self.args,
            kwargs=self.kwargs)

    def get_success_url(self):
        return str(self.__get_redirect_url())
