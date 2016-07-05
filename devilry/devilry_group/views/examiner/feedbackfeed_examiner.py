# Python imports
from __future__ import unicode_literals

# Django imports
from datetime import datetime
from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils import timezone
from django_cradmin import crapp
from django.utils.translation import ugettext_lazy as _, ugettext_lazy, pgettext_lazy

# Devilry/cradmin imports
from django_cradmin.viewhelpers import delete
from django_cradmin.viewhelpers import update
from django_cradmin.crispylayouts import PrimarySubmit, DefaultSubmit
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget

from devilry.apps.core import models as core_models
from devilry.utils import datetimeutils
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views.cradmin_feedbackfeed_base import GroupCommentForm
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget


class AbstractFeedbackForm(GroupCommentForm):
    """
    Feedback-related forms regarding grading inherits from this.
    """
    def get_grading_points(self):
        raise NotImplementedError()


class PassedFailedFeedbackForm(AbstractFeedbackForm):
    """
    Form for passed/failed grade plugin.
    """

    #: Set delivery as passed or failed.
    passed = forms.BooleanField(
            label=pgettext_lazy('grading', 'Passed?'),
            help_text=pgettext_lazy('grading', 'Check to provide a passing grade.'),
            initial=True,
            required=False)

    @classmethod
    def get_field_layout(cls):
        return ['passed']

    def get_grading_points(self):
        if self.cleaned_data['passed']:
            return self.group.assignment.max_points
        else:
            return 0


class PointsFeedbackForm(AbstractFeedbackForm):
    """
    Form for point-based grade plugin.
    """

    #: Set points that should be given to the delivery.
    points = forms.IntegerField(
            required=True,
            min_value=0,
            label=_('Points'))

    def __init__(self, *args, **kwargs):
        super(PointsFeedbackForm, self).__init__(*args, **kwargs)
        self.fields['points'].max_value = self.group.assignment.max_points
        self.fields['points'].help_text = pgettext_lazy('grading', 'Number between 0 and %(max_points)s.') % {
            'max_points': self.group.assignment.max_points
        }

    @classmethod
    def get_field_layout(cls):
        return ['points']

    def get_grading_points(self):
        return self.cleaned_data['points']


class CreateFeedbackSetForm(GroupCommentForm):
    """
    Form for creating a new FeedbackSet (deadline).
    """
    #: Deadline to be added to the new FeedbackSet.
    deadline_datetime = forms.DateTimeField(widget=DateTimePickerWidget)

    @classmethod
    def get_field_layout(cls):
        return ['deadline_datetime']


class ExaminerBaseFeedbackFeedView(cradmin_feedbackfeed_base.FeedbackFeedBaseView):
    """
    Base view for examiner.
    """
    def get_devilryrole(self):
        """
        Get the devilryrole for the view.

        Returns:
            str: ``examiner`` as devilryrole.
        """
        return 'examiner'

    def set_automatic_attributes(self, obj):
        super(ExaminerBaseFeedbackFeedView, self).set_automatic_attributes(obj)
        obj.user_role = 'examiner'


class ExaminerFeedbackView(ExaminerBaseFeedbackFeedView):
    """
    The examiner feedbackview.
    This is the view where examiner corrects the delivery made by a student
    and is only able to create drafted comments, or publish grading.

    If the last FeedbackSet is published, this view redirects to :class:`.ExaminerFeedbackCreateFeedbackSetView`.
    See :func:`dispatch`.
    """
    template_name = 'devilry_group/feedbackfeed_examiner_feedback.django.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if the last FeedbackSet in the group is published. If it's published, a redirect response to
        :class:`~.ExaminerFeedbackCreateFeedbackSetView is returned.

        Args:
            request: request object.

        Returns:
            HttpResponse: The HTTP response.
        """
        group = self.request.cradmin_role
        # NOTE: :func:`~devilry.apps.core.models.AssignmentGroup.last_feedbackset_is_published` performs a query.
        if group.last_feedbackset_is_published:
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appurl('create-feedbackset'))
        return super(ExaminerFeedbackView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        """
        Get the correct form based on what grade plugin that is used.

        Returns:
            A :class:`devilry.devilry_group.views.cradmin_feedbackfeed_base.GroupCommentForm`

        """
        assignment = self.request.cradmin_role.assignment
        if assignment.grading_system_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            return PassedFailedFeedbackForm
        elif assignment.grading_system_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS:
            return PointsFeedbackForm
        else:
            raise ValueError('Unsupported grading_system_plugin_id: {}'.format(assignment.grading_system_plugin_id))

    def get_buttons(self):
        buttons = super(ExaminerFeedbackView, self).get_buttons()
        buttons.extend([
            DefaultSubmit('examiner_add_comment_to_feedback_draft',
                          _('Save draft and preview'),
                          css_class='btn btn-default'),
            PrimarySubmit('examiner_publish_feedback',
                          _('Publish feedback'),
                          css_class='btn btn-primary')
        ])
        return buttons

    def save_object(self, form, commit=True):
        obj = super(ExaminerFeedbackView, self).save_object(form=form)
        if obj.feedback_set.grading_published_datetime is not None:
            messages.warning(self.request, ugettext_lazy('Feedback is already published!'))
        else:
            if 'examiner_add_comment_to_feedback_draft' in self.request.POST:
                # If comment is part of a draft, the comment should only be visible to
                # the examiner until draft-publication.
                obj.visibility = group_models.GroupComment.VISIBILITY_PRIVATE
                obj.part_of_grading = True
                obj = super(ExaminerFeedbackView, self).save_object(form=form, commit=True)
            elif 'examiner_publish_feedback' in self.request.POST:
                result, error_msg = obj.feedback_set.publish(
                        published_by=obj.user,
                        grading_points=form.get_grading_points())
                if result is False:
                    messages.error(self.request, ugettext_lazy(error_msg))
                elif len(obj.text) > 0:
                    # Don't make comment visible to others unless it actually
                    # contains any text.
                    obj.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
                    obj.part_of_grading = True
                    obj.published_datetime = obj.get_published_datetime()
                    obj = super(ExaminerFeedbackView, self).save_object(form=form, commit=True)
        return obj

    def get_form_invalid_message(self, form):
        return 'Cannot publish feedback until deadline has passed!'


class ExaminerFeedbackCreateFeedbackSetView(ExaminerBaseFeedbackFeedView):
    """
    View to create a new FeedbackSet if the current last feedbackset is published.

    When a new unpublished FeedbackSet is created, this view redirects to :class:`.ExaminerFeedbackView`.
    See :func:`dispatch`.
    """
    template_name = 'devilry_group/feedbackfeed_examiner_feedback.django.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if the last FeedbackSet in the group is published. If it's published, a redirect response to
        :class:`~.ExaminerFeedbackView` is returned.

        Args:
            request (HttpRequest): request object.

        Returns:
            HttpResponse: The HTTP response.
        """
        group = self.request.cradmin_role
        # NOTE: :func:`~devilry.apps.core.models.AssignmentGroup.last_feedbackset_is_published` performs a query.
        if not group.last_feedbackset_is_published:
            return HttpResponseRedirect(self.request.cradmin_app.reverse_appindexurl())

        return super(ExaminerFeedbackCreateFeedbackSetView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        return CreateFeedbackSetForm

    def get_buttons(self):
        buttons = super(ExaminerFeedbackCreateFeedbackSetView, self).get_buttons()
        buttons.extend([
            DefaultSubmit('examiner_create_new_feedbackset',
                          _('Give new attempt'),
                          css_class='btn btn-primary'),
        ])
        return buttons

    def __create_new_feedbackset(self, comment, new_deadline):
        """
        Creates a new :class:`devilry.devilry_group.models.FeedbackSet` as long as the ``new_deadline`` is
        in the future.

        :Note: Extra constraints to the new deadline and creation of a FeedbackSet may be added.

        Args:
            comment (GroupComment): Comment to be posted with the new FeedbackSet
            new_deadline (DateTime): The deadline.

        Returns:
            FeedbackSet: returns the newly created :class:`devilry.devilry_group.models.FeedbackSet` instance.

        """
        if new_deadline <= datetimeutils.get_current_datetime():
            messages.error(self.request, ugettext_lazy('Deadline must be ahead of current date and time'))
            return None

        # Update current last feedbackset in group before
        # creating the new feedbackset.
        current_feedbackset = group_models.FeedbackSet.objects.get(id=comment.feedback_set_id)
        current_feedbackset.is_last_in_group = None
        current_feedbackset.grading_published_by = comment.user
        current_feedbackset.full_clean()
        current_feedbackset.save()

        feedbackset = group_models.FeedbackSet(
            group=self.request.cradmin_role,
            feedbackset_type=group_models.FeedbackSet.FEEDBACKSET_TYPE_NEW_ATTEMPT,
            created_by=comment.user,
            deadline_datetime=new_deadline
        )
        feedbackset.full_clean()
        feedbackset.save()
        return feedbackset

    def save_object(self, form, commit=True):
        comment = super(ExaminerFeedbackCreateFeedbackSetView, self).save_object(form=form)

        if 'deadline_datetime' in self.request.POST:
            new_deadline = datetime.strptime(self.request.POST['deadline_datetime'], '%Y-%m-%d %H:%M')

            new_feedbackset = self.__create_new_feedbackset(comment=comment, new_deadline=new_deadline)
            if new_feedbackset is None:
                return comment

            if len(comment.text) > 0:
                # Also save comment and set the comments feedback_set to the newly
                # created new_feedbackset.
                comment.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
                comment.feedback_set = new_feedbackset
                comment.published_datetime = new_feedbackset.created_datetime + timezone.timedelta(seconds=1)
                comment = super(ExaminerFeedbackCreateFeedbackSetView, self).save_object(form=form, commit=True)
        return comment


class ExaminerDiscussView(ExaminerBaseFeedbackFeedView):
    """
    The examiner discussview.
    This is the view examiner uses for communicating with students and admins in the feedbackfeed.
    """
    template_name = 'devilry_group/feedbackfeed_examiner_discuss.django.html'

    def get_buttons(self):
        buttons = super(ExaminerDiscussView, self).get_buttons()
        buttons.extend([
            PrimarySubmit('examiner_add_comment_for_examiners',
                          _('Add comment for examiners'),
                          css_class='btn btn-default'),
            DefaultSubmit('examiner_add_public_comment',
                          _('Add public comment'),
                          css_class='btn btn-primary'),
        ])
        return buttons

    def save_object(self, form, commit=True):
        obj = super(ExaminerDiscussView, self).save_object(form)
        self._convert_temporary_files_to_comment_files(form, obj)
        if form.data.get('examiner_add_comment_for_examiners'):
            obj.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
            obj.published_datetime = timezone.now()
        elif form.data.get('examiner_add_public_comment'):
            obj.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
            obj.published_datetime = timezone.now()

        obj = super(ExaminerDiscussView, self).save_object(form, commit=True)
        return obj

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appurl(viewname='discuss')


class GroupCommentDeleteView(delete.DeleteView):
    """
    View to delete an existing groupcomment with visibility set to private.
    When a groupcomment has visibility set to private, this means it's a feedbackdraft.
    """
    model = group_models.GroupComment

    def get_queryset_for_role(self, role):
        """
        Filter out :obj:`~devilry.devilry_group.models.GroupComment`s based on the role of role of the
        crinstance and the primarykey of the comment since in this case only a single comment should be fetched.

        Args:
            role (GroupComment): The roleclass for the crinstance.

        Returns:
            QuerySet: Set containing one :obj:`~devilry.devilry_group.models.GroupComment`.
        """
        return group_models.GroupComment.objects.filter(
                feedback_set__group=role,
                id=self.kwargs.get('pk'))

    def get_object_preview(self):
        return 'Groupcomment'

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()


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


class GroupCommentEditView(update.UpdateView):
    """
    View to edit an existing feedback draft.

    Makes it possible for an Examiner to edit the ``text``-attribute value of a
    :class:`~devilry.devilry_group.models.GroupComment` that's saved as a draft.
    """
    model = group_models.GroupComment

    def get_queryset_for_role(self, role):
        """
        Filter out :obj:`~devilry.devilry_group.models.GroupComment`s based on the role of role of the
        crinstance and the primarykey of the comment since in this case only a single comment should be fetched.

        Args:
            role (GroupComment): The roleclass for the crinstance.

        Returns:
            QuerySet: Set containing one :obj:`~devilry.devilry_group.models.GroupComment`.
        """
        return group_models.GroupComment.objects.filter(
                feedback_set__group=role,
                id=self.kwargs.get('pk'))

    def get_form_class(self):
        """
        Get the formclass to use.

        Returns:
            EditGroupCommentForm: The form class.
        """
        return EditGroupCommentForm

    def get_form(self, form_class=None):
        """
        Set ``AceMarkdownWidget`` on the text form field and do not show the field label.
        Args:
            form_class: Defaults to None

        Returns:
            EditGroupCommentForm: Form with field-representations set.
        """
        form = super(GroupCommentEditView, self).get_form(form_class=form_class)
        form.fields['text'].widget = AceMarkdownWidget()
        form.fields['text'].label = False
        return form

    def get_field_layout(self):
        """
        Override get field layout as we're using ``AceMarkdownWidget`` to define
        the form field in our form class :class:`~.EditGroupCommentForm`.

        Returns:
            list: List extended with the field layout of :class:`~.EditGroupCommentForm`.
        """
        field_layout = []
        field_layout.extend(self.get_form_class().get_field_layout())
        return field_layout

    def save_object(self, form, commit=True):
        """
        Save the edited :obj:`~devilry.devilry_group.models.GroupComment`.

        Args:
            form: The :class:`~.EditGroupCommentForm` passed.
            commit: Should it be saved? (Defaults to True)

        Returns:
            GroupComment: The saved comment.
        """
        comment = super(GroupCommentEditView, self).save_object(form=form, commit=commit)
        self.add_success_messages('GroupComment updated!')
        return comment

    def get_success_url(self):
        """
        The success url is for this view if the user wants to continue editing, else it redirects to
        the indexview, :class:`~.ExaminerFeedbackView`.

        Returns:
            url: Redirected to view for that url.
        """
        if self.get_submit_save_and_continue_edititing_button_name() in self.request.POST:
            return self.request.cradmin_app.reverse_appurl(
                'groupcomment-edit',
                args=self.args,
                kwargs=self.kwargs)
        else:
            return self.request.cradmin_app.reverse_appindexurl()


class App(crapp.App):
    appurls = [
        crapp.Url(
                r'^$',
                ExaminerFeedbackView.as_view(),
                name=crapp.INDEXVIEW_NAME),
        crapp.Url(
                r'^discuss$',
                ExaminerDiscussView.as_view(),
                name='discuss'),
        crapp.Url(
                r'^create-feedbackset$',
                ExaminerFeedbackCreateFeedbackSetView.as_view(),
                name='create-feedbackset'),
        crapp.Url(
                r'^groupcomment-delete/(?P<pk>\d+)$',
                GroupCommentDeleteView.as_view(),
                name="groupcomment-delete"),
        crapp.Url(
                r'^groupcomment-edit/(?P<pk>\d+)$',
                GroupCommentEditView.as_view(),
                name='groupcomment-edit'),
    ]
