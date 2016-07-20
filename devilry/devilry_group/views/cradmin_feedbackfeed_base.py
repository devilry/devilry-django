# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports
import json
import datetime

# Django imports
from django import forms
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

# Devilry/cradmin imports
from devilry.devilry_group.timeline_builder import builder_base
from devilry.devilry_cradmin.devilry_listbuilder import feedbackfeed_timeline
from devilry.devilry_cradmin.devilry_listbuilder import feedbackfeed_sidebar
from devilry.devilry_group import models as group_models
from devilry.devilry_comment import models as comment_models
from devilry.devilry_group.timeline_builder import feedbackfeed_timelinebuilder
from devilry.devilry_group.timeline_builder import feedbackfeed_sidebarbuilder
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget
from django_cradmin.viewhelpers import create

# 3rd party imports
from crispy_forms import layout
from xml.sax.saxutils import quoteattr


class GroupCommentForm(forms.ModelForm):
    """
    Model form for :class:`~devilry.apps.core.models.AssignmentGroup`
    """
    class Meta:
        fields = ['text']
        model = group_models.GroupComment

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        super(GroupCommentForm, self).__init__(*args, **kwargs)

    @classmethod
    def get_field_layout(cls):
        return []


class FeedbackFeedBaseView(create.CreateView):
    """
    Base feedbackfeed view.
    The feedbackfeed view handles the options a certain devilryrole(``student``, ``examiner``, 'someadmin') should have
    when the feedbackfeed view is rendered. Specialized views for each devilryrole must subclasses this class.
    """
    template_name = "devilry_group/feedbackfeed.django.html"
    model = group_models.GroupComment
    form_attributes = {
        'django-cradmin-bulkfileupload-form': ''
    }

    submit_use_label = _('Post comment')

    class Meta:
        abstract = True

    def get_devilryrole(self):
        """
        Get the devilryrole of a user.
        This function must be implemnted by a subclass.

        Raises:
            NotImplementedError: Raised if not implemented by subclass.
        """
        raise NotImplementedError('Must be implemented in subclass')

    def get_form_class(self):
        return GroupCommentForm

    def get_form_kwargs(self):
        kwargs = super(FeedbackFeedBaseView, self).get_form_kwargs()
        group = self.request.cradmin_role
        kwargs['group'] = group
        return kwargs

    def __build_timeline(self, feedbackset_queryset):
        """
        Building the timeline which includes all the events that occur in the feedbackfeed in
        the order that they occur.
        For more details, See :class:`devilry.devilry_group.feedbackfeed_timeline_builder.FeedbackFeedTimelineBuilder`

        Returns:
             :obj:`devilry.devilry_group.timeline_builder.FeedbackFeedTimelineBuilder`: Built timeline.
        """
        timeline_builder = feedbackfeed_timelinebuilder.FeedbackFeedTimelineBuilder(
                feedbacksets=feedbackset_queryset,
                group=self.request.cradmin_role)
        timeline_builder.build()
        return timeline_builder

    def __build_sidebar(self, feedbackset_queryset):
        """

        Returns:
            :obj:`devilry.devilry_group.timeline_builder.FeedbackFeedSidebarBuilder`
        """
        sidebar_builder = feedbackfeed_sidebarbuilder.FeedbackFeedSidebarBuilder(
            feedbacksets=feedbackset_queryset
        )
        sidebar_builder.build()
        return sidebar_builder

    def get_context_data(self, **kwargs):
        """
        Sets the context data needed to render elements in the template.

        Args:
            **kwargs (dict): Parameters to get_context_data.

        Returns:
             dict: The context data dictionary.
        """
        context = super(FeedbackFeedBaseView, self).get_context_data(**kwargs)
        context['devilry_ui_role'] = self.get_devilryrole()
        context['subject'] = self.request.cradmin_role.assignment.period.subject
        context['assignment'] = self.request.cradmin_role.assignment
        context['period'] = self.request.cradmin_role.assignment.period

        # Build the timeline for the feedbackfeed
        builder_queryset = builder_base.get_feedbackfeed_builder_queryset(
                self.request.cradmin_role,
                self.request.user,
                self.get_devilryrole())
        built_timeline = self.__build_timeline(builder_queryset)
        context['last_deadline'] = built_timeline.get_last_deadline()
        context['timeline'] = built_timeline.timeline
        context['feedbacksets'] = built_timeline.feedbacksets
        context['last_feedbackset'] = built_timeline.get_last_feedbackset()
        context['current_date'] = datetime.datetime.now()
        context['listbuilder_list'] = feedbackfeed_timeline.TimelineListBuilderList.from_built_timeline(
            built_timeline,
            group=self.request.cradmin_role,
            devilryrole=self.get_devilryrole(),
            assignment=context['assignment']
        )

        # Build the sidebar using the fetched data from timelinebuilder
        built_sidebar = self.__build_sidebar(builder_queryset)
        context['sidebarbuilder_list'] = feedbackfeed_sidebar.SidebarListBuilderList.from_built_sidebar(
            built_sidebar,
            group=self.request.cradmin_role,
            devilryrole=self.get_devilryrole(),
            assignment=context['assignment']
        )
        return context

    def get_button_layout(self):
        """
        Get the button layout. This is added to the crispy form layout.

        Defaults to a :class:`crispy_forms.layout.Div` with css class
        ``django_cradmin_submitrow`` containing all the buttons
        returned by :meth:`.get_buttons`.

        Returns:
            list: List of buttons.
        """
        return [
        ]

    def get_buttons(self):
        return []

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
        """
        How post of the should be handled. This can be handled more specifically in subclasses.
        Should add a call to super in the subclass implementation on override.

        Args:
            form (GroupCommentForm): Form thats passed on post.
            commit (bool): If form-object(:class:`~devilry.devilry_group.models.GroupComment`) should be saved.

        Returns:
            GroupComment: The form-object :class:`~devilry.devilry_group.models.GroupComment`.
        """
        obj = super(FeedbackFeedBaseView, self,).save_object(form, commit=commit)
        return obj

    def get_collectionqueryset(self):
        """
        Get a set of files from cradmins ``temporary fileuploadstore``.

        Returns:
            QuerySet: ``django_cradmin.TemporaryFileCollection`` objects.
        """
        return TemporaryFileCollection.objects \
            .filter_for_user(self.request.user) \
            .prefetch_related('files')

    def _convert_temporary_files_to_comment_files(self, form, groupcomment):
        """
        Converts files added to a comment to :obj:`~devilry.devilry_comment.models.CommentFile`.
        See :func:`~devilry.devilry_comment.models.CommentFile.add_comment_from_temporary_file`.

        Args:
            form (GroupCommentForm): :class:`~.GroupCommentForm` instance passed on post.
            groupcomment (GroupComment): :class:`~devilry.devilry_group.models.GroupComment` instance posted.

        Returns:
            bool: False if files does not exist, else True.

        """
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
