# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from xml.sax.saxutils import quoteattr

from crispy_forms import layout
from django import forms
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection
from django_cradmin.viewhelpers import create

from devilry.apps.core.models import Assignment
from devilry.devilry_comment import models as comment_models
from devilry.devilry_cradmin import devilry_acemarkdown
from devilry.devilry_cradmin.devilry_listbuilder import feedbackfeed_sidebar
from devilry.devilry_cradmin.devilry_listbuilder import feedbackfeed_timeline
from devilry.devilry_group import models as group_models
from devilry.devilry_group.feedbackfeed_builder import builder_base
from devilry.devilry_group.feedbackfeed_builder import feedbackfeed_sidebarbuilder
from devilry.devilry_group.feedbackfeed_builder import feedbackfeed_timelinebuilder
from devilry.utils import datetimeutils


class GroupCommentForm(forms.ModelForm):
    """
    Abstract class for creating a :obj:`~.devilry.devilry_group.models.GroupComment`.

    Defines the attributes for the ``GroupComment`` form.

    Examples:

        If you want to provide a check on the form data before save, just subclass this and
        add your custom clean logic::

            class StandardGroupCommentForm(GroupCommentForm):

                def clean(self):
                    super(GroupCommentForm, self).clean()
                    if len(self.cleaned_data['text']) == 0 and self.cleaned_data['temporary_file_collection_id'] is None:
                        raise ValidationError({
                          'text': ugettext_lazy('A comment must have either text or a file attached, or both.'
                                                ' An empty comment is not allowed.')
                        })

    """
    class Meta:
        fields = ['text']
        model = group_models.GroupComment

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group')
        self.feedback_set = kwargs.pop('feedback_set')
        super(GroupCommentForm, self).__init__(*args, **kwargs)
        self.instance.feedback_set = self.feedback_set

    @classmethod
    def get_field_layout(cls):
        return []


class StandardGroupCommentForm(GroupCommentForm):
    """
    This should be used by all views that requires the comment to either contain a file/files OR text.

    Failing to provide file/files or text will result in an error message. This is handled in clean.
    """
    def clean(self):
        super(GroupCommentForm, self).clean()
        if len(self.cleaned_data['text']) == 0 and self.cleaned_data['temporary_file_collection_id'] is None:
            raise ValidationError({
              'text': ugettext_lazy('A comment must have either text or a file attached, or both.'
                                    ' An empty comment is not allowed.')
            })


class FeedbackFeedBaseView(create.CreateView):
    """
    Base feedbackfeed view.

    The feedbackfeed view handles the options a certain devilryrole(``student``, ``examiner``, 'someadmin') should have
    when the feedbackfeed view is rendered. Specialized views for each devilryrole must subclasses this class.
    """
    template_name = "devilry_group/feedbackfeed.django.html"
    model = group_models.GroupComment
    form_attributes = {
        'django-cradmin-bulkfileupload-form': '',
        'django-cradmin-bulkfileupload-form-prevent-window-dragdrop': 'true'
    }
    submit_use_label = _('Post comment')

    class Meta:
        abstract = True

    def __should_disable_comment_form(self, request):
        """
        Check if the file upload and comment form should be disabled.

        Returns a message string or None.
        """
        group = self.assignment_group
        user_role = request.cradmin_instance.get_devilryrole_for_requestuser()
        if user_role.endswith('admin'):
            user_role = group_models.GroupComment.USER_ROLE_ADMIN
        try:
            group.cached_data.last_feedbackset.can_add_comment(assignment=group.parentnode, comment_user_role=user_role)
        except (group_models.HardDeadlineExpiredException, group_models.PeriodExpiredException) as e:
            return e.message
        return None

    def post(self, request, *args, **kwargs):
        disable_comment_form_message = self.__should_disable_comment_form(request=request)
        if disable_comment_form_message:
            messages.warning(request=request, message=disable_comment_form_message)
            return HttpResponseRedirect(request.path_info)
        return super(FeedbackFeedBaseView, self).post(request=request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.form_disabled_message = self.__should_disable_comment_form(request=request)
        return super(FeedbackFeedBaseView, self).get(request=request, *args, **kwargs)

    @property
    def assignment_group(self):
        return self.request.cradmin_role

    def get_devilryrole(self):
        """
        Get the devilryrole of a user.
        This function must be implemented by a subclass.

        Raises:
            NotImplementedError: Raised if not implemented by subclass.
        """
        raise NotImplementedError('Must be implemented in subclass')

    def get_form_class(self):
        return StandardGroupCommentForm

    def get_form_kwargs(self):
        kwargs = super(FeedbackFeedBaseView, self).get_form_kwargs()
        group = self.assignment_group
        kwargs['group'] = group
        kwargs['feedback_set'] = group.cached_data.last_feedbackset
        return kwargs

    def __build_timeline(self, assignment, feedbackset_queryset):
        """
        Building the timeline which includes all the events that occur in the feedbackfeed in
        the order that they occur.
        For more details, See :class:`devilry.devilry_group.feedbackfeed_timeline_builder.FeedbackFeedTimelineBuilder`

        Returns:
             :obj:`devilry.devilry_group.feedbackfeed_builder.FeedbackFeedTimelineBuilder`: Built timeline.
        """
        timeline_builder = feedbackfeed_timelinebuilder.FeedbackFeedTimelineBuilder(
                assignment=assignment,
                feedbacksets=feedbackset_queryset,
                group=self.assignment_group)
        timeline_builder.build()
        return timeline_builder

    def __build_sidebar(self, assignment, feedbackset_queryset):
        """
        Building the sidebar that includes the files for each comment, and comments for each
        FeedbackSet.

        Returns:
            :obj:`devilry.devilry_group.feedbackfeed_builder.FeedbackFeedSidebarBuilder`
        """
        sidebar_builder = feedbackfeed_sidebarbuilder.FeedbackFeedSidebarBuilder(
            assignment=assignment,
            feedbacksets=feedbackset_queryset,
            group=self.assignment_group)
        sidebar_builder.build()
        return sidebar_builder

    def __get_assignment(self):
        group = self.assignment_group
        return Assignment.objects\
            .prefetch_related(
                'assignmentgroups'
            )\
            .filter(id=group.assignment.id)\
            .prefetch_point_to_grade_map().first()

    def __get_form_disabled(self):
        """
        Helper function.

        Attribute ``form_disabled_message`` is set when method ``get`` is called and
        the form should be disabled.

        Returns ``True`` or ``False``
        """
        if hasattr(self, 'form_disabled_message'):
            return self.form_disabled_message is not None
        return False

    def __get_form_disabled_message(self):
        """
        Helper function.

        Attribute ``form_disabled_message`` is set when method ``get`` is called and
        the form should be disabled.

        Returns message string or ``None``.
        """
        if hasattr(self, 'form_disabled_message'):
            return self.form_disabled_message
        return None

    def get_hard_deadline_info_text(self):
        """
        Get hard deadline info text. Must be implemented in subclasses.

        Uses function ``get_devilry_hard_deadline_info_text``.

        Returns:
            str: info text.
        """
        raise NotImplementedError()

    def get_context_data(self, **kwargs):
        """
        Sets the context data needed to render elements in the template.

        Args:
            **kwargs (dict): Parameters to get_context_data.

        Returns:
             dict: The context data dictionary.
        """
        context = super(FeedbackFeedBaseView, self).get_context_data(**kwargs)
        assignment = self.__get_assignment()
        group = self.assignment_group

        # Build the timeline for the feedbackfeed
        builder_queryset = builder_base.get_feedbackfeed_builder_queryset(
                group,
                self.request.user,
                self.get_devilryrole())

        built_timeline = self.__build_timeline(assignment, builder_queryset)
        last_feedbackset = group.cached_data.last_feedbackset
        context['devilry_ui_role'] = self.get_devilryrole()
        context['group'] = group
        context['num_students_in_group'] = group.candidates.count()
        context['subject'] = assignment.period.subject
        context['period'] = assignment.period
        context['assignment'] = assignment
        context['last_deadline'] = last_feedbackset.deadline_datetime
        context['last_feedbackset'] = last_feedbackset
        context['current_date'] = timezone.now()
        context['last_deadline_as_string'] = datetimeutils\
            .datetime_to_url_string(last_feedbackset.deadline_datetime)
        context['listbuilder_list'] = feedbackfeed_timeline.TimeLineListBuilderList.from_built_timeline(
            built_timeline,
            group=group,
            devilryrole=self.get_devilryrole(),
            assignment=assignment,
            requestuser=self.request.user
        )
        context['assignment_uses_hard_deadlines'] = assignment.deadline_handling_is_hard()
        context['assignment_uses_hard_deadlines_info_text'] = self.get_hard_deadline_info_text()
        context['students_can_create_groups'] = assignment.students_can_create_groups_now
        context['comment_form_disabled'] = self.__get_form_disabled()
        context['comment_form_disabled_message'] = self.__get_form_disabled_message()

        # Build the sidebar using the fetched data from timelinebuilder
        if self.get_available_commentfile_count_for_user() > 0:
            built_sidebar = self.__build_sidebar(assignment, builder_queryset)
            context['sidebarbuilder_list'] = feedbackfeed_sidebar.SidebarListBuilderList.from_built_sidebar(
                built_sidebar,
                group=group,
                devilryrole=self.get_devilryrole(),
                assignment=context['assignment']
            )
        else:
            context['sidebarbuilder_list'] = None

        return context

    def get_available_commentfile_count_for_user(self):
        """
        Get the total amount of CommentFiles available for the student.

        Returns:
            (int): Count of CommentFiles available for the user.
        """
        group = self.assignment_group
        group_comment_queryset = group_models.GroupComment.objects\
            .filter(feedback_set__group=group)\
            .exclude_private_comments_from_other_users(user=self.request.user)\
            .exclude_is_part_of_grading_feedbackset_unpublished()

        if self.get_devilryrole() == 'student':
            group_comment_queryset = group_comment_queryset\
                .exclude(visibility=group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)

        comment_file_queryset = comment_models.CommentFile.objects\
            .filter(comment_id__in=group_comment_queryset.values_list('id', flat=True))

        return comment_file_queryset.count()

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

    def get_form_heading_text_template_name(self):
        """
        Get template for rendering a heading text in the form.

        Override this to provide an explanatory text added to the heading of the form
        for posting a comment. This should include some information about what happens
        when a comment is posted.

        Returns:
            (str): a string or path to html template or None.
        """
        return None

    def _get_form_heading_text(self):
        """
        Loads information text for the comment form.

        Returns:
            (str): a rendered string(with render_to_string()) or None.
        """
        template_name = self.get_form_heading_text_template_name()
        if template_name:
            return render_to_string(template_name=template_name)
        else:
            return None

    def get_field_layout(self):
        field_layout = []
        heading_text = self._get_form_heading_text()
        if heading_text:
            field_layout.append(layout.Div(
                layout.HTML(heading_text),
                css_class='devilry-group-feedbackfeed-form-heading'
            ))
        field_layout.extend(self.get_form_class().get_field_layout())
        field_layout.append('text')
        field_layout.append(
            layout.Div(
                layout.HTML(render_to_string(
                    'devilry_group/include/fileupload.django.html',
                    {
                        "apiparameters": quoteattr(json.dumps({
                            "autosubmit": False,
                            "uploadapiurl": reverse('cradmin_temporary_file_upload_api'),
                            "unique_filenames": True,
                            "max_filename_length": comment_models.CommentFile.MAX_FILENAME_LENGTH,
                            "errormessage503": "Server timeout while uploading the file. "
                                               "This may be caused by a poor upload link and/or a too large file.",
                            "apiparameters": {
                                "singlemode": False,
                            },
                        })),
                        "hiddenfieldname": "temporary_file_collection_id",

                    })),
                # css_class='panel-footer'
            ))
        return [
            layout.Div(
                layout.Div(
                    *field_layout
                ),
                layout.Div(
                    *self.get_buttons(),
                    css_class="text-right"
                ),
                css_class='comment-form-container'
            )
        ]

    def get_acemarkdown_widget_class(self):
        return devilry_acemarkdown.Default

    def get_form(self, form_class=None):
        form = super(FeedbackFeedBaseView, self).get_form(form_class=form_class)
        form.fields['text'].widget = self.get_acemarkdown_widget_class()()
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
        How post of the comment should be handled. This can be handled more specifically in subclasses.

        Add call to super in the subclass implementation on override.

        Args:
            form (GroupCommentForm): Posted form.
            commit (bool): If form-object(:class:`~devilry.devilry_group.models.GroupComment`) should be saved.

        Returns:
            GroupComment: The form-object :class:`~devilry.devilry_group.models.GroupComment`.
        """
        groupcomment = super(FeedbackFeedBaseView, self,).save_object(form, commit=commit)
        if commit:
            self._convert_temporary_files_to_comment_files(form, groupcomment)
        if commit and groupcomment.id:
            self.perform_after_save(comment=groupcomment)
        return groupcomment

    def perform_after_save(self, comment):
        """
        This method is called if the comment posted is saved and commit is ``True``.
        This means that both the comment and files uploaded with it is saved in the database.

        Override this function for operations that require that the comment is saved, such
        as email sending etc.
        """

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
            groupcomment.add_commentfile_from_temporary_file(tempfile=temporaryfile)

        return True

    def get_success_message(self, object):
        return _('Comment added!')
