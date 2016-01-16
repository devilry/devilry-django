# Django imports
from django import forms
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# Python imports
import json
import datetime

# Devilry/cradmin imports
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models

# 3rd party imports
from crispy_forms import layout
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget
from django_cradmin.viewhelpers import create
from xml.sax.saxutils import quoteattr
from devilry.devilry_group.timeline_builder import feedbackfeed_timeline_builder


class GroupCommentForm(forms.ModelForm):

    class Meta:
        fields = ['text']
        model = group_models.GroupComment

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        super(GroupCommentForm, self).__init__(*args, **kwargs)

    @classmethod
    def get_field_layout(self):
        return []


class FeedbackFeedBaseView(create.CreateView):
    template_name = "devilry_group/feedbackfeed.django.html"

    # for cradmin CreateView
    model = group_models.GroupComment
    form_attributes = {
        'django-cradmin-bulkfileupload-form': ''
    }

    def get_form_class(self):
        return GroupCommentForm

    def get_form_kwargs(self):
        kwargs = super(FeedbackFeedBaseView, self).get_form_kwargs()
        group = self.request.cradmin_role
        kwargs['group'] = group
        return kwargs

    def _get_comments_for_group(self, group):
        raise NotImplementedError("Subclasses must implement _get_queryset_for_group!")

    def get_context_data(self, **kwargs):
        context = super(FeedbackFeedBaseView, self).get_context_data(**kwargs)
        timelime_builder = feedbackfeed_timeline_builder.FeedbackFeedTimelineBuilder(self)
        context['subject'] = self.request.cradmin_role.assignment.period.subject
        context['assignment'] = self.request.cradmin_role.assignment
        context['period'] = self.request.cradmin_role.assignment.period
        feedbacksets = timelime_builder.get_feedbacksets_for_group(self.request.cradmin_role)
        context['last_deadline'], context['timeline'] = timelime_builder.build_timeline(self.request.cradmin_role, feedbacksets)
        context['feedbacksets'] = feedbacksets
        try:
            context['last_feedbackset'] = feedbacksets[0]
        except IndexError:
            pass
        context['current_date'] = datetime.datetime.now()

        return context

    submit_use_label = _('Post comment')

    def get_button_layout(self):
        """
        Get the button layout. This is added to the crispy form layout.

        Defaults to a :class:`crispy_forms.layout.Div` with css class
        ``django_cradmin_submitrow`` containing all the buttons
        returned by :meth:`.get_buttons`.
        """
        return [
        ]

    def get_buttons(self):
        raise NotImplementedError("Subclasses must implement get_buttons!")

    def get_field_layout(self):
        field_layout = []
        field_layout.extend(self.get_form_class().get_field_layout())
        field_layout.append('text')
        field_layout.append(
            layout.Div(
                layout.HTML(render_to_string(
                    'devilry_group/include/fileupload.django.html',
                    {
                        "apiparameters": quoteattr(json.dumps({
                            "unique_filenames": True,
                            "max_filename_length": comment_models.CommentFile.MAX_FILENAME_LENGTH
                        })),
                        "hiddenfieldname": "temporary_file_collection_id",
                        "apiurl": reverse('cradmin_temporary_file_upload_api')
                    })),
                # css_class='panel-footer'
            ))
        return [
            layout.Fieldset(
                '',
                layout.Div(
                    *field_layout
                ),
                layout.Div(
                    layout.Div(*self.get_buttons()),
                    css_class="text-right"
                ),
                css_class='comment-form-container'
            )
        ]

    def get_form(self, form_class=None):
        form = super(FeedbackFeedBaseView, self).get_form(form_class=form_class)
        form.fields['text'].widget = AceMarkdownWidget()
        form.fields['text'].label = False
        form.fields['temporary_file_collection_id'] = forms.IntegerField(required=False)
        return form

    def set_automatic_attributes(self, obj):
        super(FeedbackFeedBaseView, self).set_automatic_attributes(obj)
        obj.user = self.request.user
        obj.comment_type = 'groupcomment'
        obj.feedback_set = self.request.cradmin_role.feedbackset_set.latest('created_datetime')

    def save_object(self, form, commit=False):
        # if commit:
        #     raise NotImplementedError('Must be implemented by subclass!')

        obj = super(FeedbackFeedBaseView, self,).save_object(form, commit=commit)
        # self._convert_temporary_files_to_comment_files(form, obj)
        return obj

    def get_collectionqueryset(self):
        return TemporaryFileCollection.objects \
            .filter_for_user(self.request.user) \
            .prefetch_related('files')

    def _convert_temporary_files_to_comment_files(self, form, groupcomment):
        filecollection_id = form.cleaned_data.get('temporary_file_collection_id')
        if not filecollection_id:
            return False
        try:
            temporaryfilecollection = self.get_collectionqueryset().get(id=filecollection_id)
        except TemporaryFileCollection.DoesNotExist:
            return False

        for temporaryfile in temporaryfilecollection.files.all():
            print "creating commentfile for file: {}".format(temporaryfile.filename)
            groupcomment.add_commentfile_from_temporary_file(tempfile=temporaryfile)

        return True

    def get_success_message(self, object):
        return None
