# Django imports
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django import http
from django.core.urlresolvers import reverse
from django import forms

# Python imports
import json
import datetime
import collections

# Devilry/cradmin imports
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models

# 3rd party imports
from crispy_forms import layout
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget
from django_cradmin.viewhelpers import create
from xml.sax.saxutils import quoteattr
from devilry.devilry_group.views import feedbackfeed_timeline_builder


class FeedbackFeedBaseView(create.CreateView):
    template_name = "devilry_group/feedbackfeed.django.html"

    # for cradmin CreateView
    model=group_models.GroupComment
    fields=["text"]
    form_attributes = {
        'django-cradmin-bulkfileupload-form': ''
    }

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
        return [
            layout.Fieldset(
                '',
                layout.Div(
                    layout.Div(
                        'text',
                        # css_class='panel-body'
                    ),
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
                    ),
                    # css_class='panel panel-default'
                ),
                layout.Div(
                    layout.Div(*self.get_buttons()),
                    css_class="col-xs-12 text-right"
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

    def save_object(self, form, commit=False):
        if commit:
            raise NotImplementedError('Must be implemented by subclass!')

        assignment_group = self.request.cradmin_role
        user = self.request.user
        time = datetime.datetime.now()

        object = form.save(commit=False)
        object.user = user
        object.comment_type = 'groupcomment'
        object.feedback_set = assignment_group.feedbackset_set.latest('created_datetime')
        object.grading_published_datetime = time

        return object

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



