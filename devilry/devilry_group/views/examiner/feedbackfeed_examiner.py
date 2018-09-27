# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crispy_forms import layout
from django import forms
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext_lazy, pgettext_lazy
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View
from django_cradmin import crapp
from django_cradmin.crispylayouts import PrimarySubmit, DefaultSubmit
from django_cradmin.viewhelpers import update, delete
from django_cradmin.widgets.datetimepicker import DateTimePickerWidget

from devilry.apps.core.models import Assignment
from devilry.apps.core import models as core_models
from devilry.devilry_cradmin import devilry_acemarkdown
from devilry.devilry_group import models as group_models
from devilry.devilry_group.views import cradmin_feedbackfeed_base
from devilry.devilry_email.feedback_email import feedback_email
from devilry.devilry_email.comment_email import comment_email
from devilry.devilry_group.views.group_comment_edit_base import EditGroupCommentBase
from devilry.utils import setting_utils


class AbstractFeedbackForm(cradmin_feedbackfeed_base.GroupCommentForm):
    """
    Feedback-related forms regarding grading or creating a new FeedbackSet inherits from this.
    """
    def get_grading_points(self):
        raise NotImplementedError()


class PassedFailedFeedbackForm(AbstractFeedbackForm):
    """
    Form for passed/failed grade plugin.
    """

    #: Set delivery as passed or failed.
    passed = forms.ChoiceField(
        choices=(
            ('Passed', ugettext_lazy('Passed')),
            ('Failed', ugettext_lazy('Failed'))
        ),
        label=pgettext_lazy('grading', 'Grade'),
        help_text=pgettext_lazy('grading', 'Choose grade'),
        required=True,
        initial=''
    )

    @classmethod
    def get_field_layout(cls):
        return ['passed']

    def get_grading_points(self):
        if self.cleaned_data['passed'] == 'Passed':
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


class CreateFeedbackSetForm(cradmin_feedbackfeed_base.GroupCommentForm):
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
    def get_hard_deadline_info_text(self):
        return setting_utils.get_devilry_hard_deadline_info_text(
            setting_name='DEVILRY_HARD_DEADLINE_INFO_FOR_EXAMINERS_AND_ADMINS')

    def get_devilryrole(self):
        """
        Get the devilryrole for the view.

        Returns:
            str: ``examiner`` as devilryrole.
        """
        return 'examiner'

    def get_acemarkdown_widget_class(self):
        return devilry_acemarkdown.Large

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
    template_name = 'devilry_group/feedbackfeed_examiner/feedbackfeed_examiner_feedback.django.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if the last FeedbackSet in the group is published. If it's published, a redirect response to
        :class:`.ExaminerFeedbackCreateFeedbackSetView` is returned.

        Args:
            request: request object.

        Returns:
            HttpResponse: The HTTP response.
        """
        group = self.request.cradmin_role
        # NOTE: `devilry.apps.core.models.AssignmentGroup.last_feedbackset_is_published` performs a query.
        if group.last_feedbackset_is_published:
            raise Http404
        return super(ExaminerFeedbackView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        """
        Get the correct form based on what grade plugin that is used.

        Returns:
            A :class:`.devilry.devilry_group.views.cradmin_feedbackfeed_base.GroupCommentForm`
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

    def _add_feedback_draft(self, form, group_comment):
        """
        Sets :obj:`devilry.devilry_group.models.GroupComment.visibility` to ``private`` and
        :obj:`devilry.devilry_group.models.GroupComment.part_of_grading` to ``True``.

        Args:
            group_comment: :class:`.devilry.devilry_group.models.GroupComment` object.

        Returns:
            (:class:`.devilry.devilry_group.models.GroupComment`): The updated object.
        """
        if form.cleaned_data['temporary_file_collection_id'] or len(group_comment.text) > 0:
            group_comment.visibility = group_models.GroupComment.VISIBILITY_PRIVATE
            group_comment.part_of_grading = True
            group_comment = super(ExaminerFeedbackView, self).save_object(form=form, commit=True)
        return group_comment

    def _publish_feedback(self, form, feedback_set, user):
        # publish FeedbackSet
        result, error_msg = feedback_set.publish(
            published_by=user,
            grading_points=form.get_grading_points())
        if result is False:
            messages.error(self.request, ugettext_lazy(error_msg))
        else:
            feedback_email.send_feedback_created_email(
                feedback_set=feedback_set, points=form.get_grading_points(),
                domain_url_start=self.request.build_absolute_uri('/')
            )

    def save_object(self, form, commit=False):
        comment = super(ExaminerFeedbackView, self).save_object(form=form)
        if comment.feedback_set.grading_published_datetime is not None:
            messages.warning(self.request, ugettext_lazy('Feedback is already published!'))
        else:
            if 'examiner_add_comment_to_feedback_draft' in self.request.POST:
                # If comment is part of a draft, the comment should only be visible to
                comment = self._add_feedback_draft(form=form, group_comment=comment)
            elif 'examiner_publish_feedback' in self.request.POST:
                # Add comment or files provided as draft, and let FeedbackSet handle the publishing.
                comment = self._add_feedback_draft(form=form, group_comment=comment)
                self._publish_feedback(form=form, feedback_set=comment.feedback_set, user=comment.user)
        return comment

    def get_form_invalid_message(self, form):
        return 'Cannot publish feedback until deadline has passed!'


class ExaminerPublicDiscussView(ExaminerBaseFeedbackFeedView):
    """
    View for discussing with everyone on the group.

    All comments posted here are visible to everyone that has access to the group.
    """
    template_name = 'devilry_group/feedbackfeed_examiner/feedbackfeed_examiner_discuss.django.html'

    def get_form_heading_text_template_name(self):
        return 'devilry_group/include/examiner_commentform_discuss_public_headingtext.django.html'

    def get_buttons(self):
        buttons = super(ExaminerPublicDiscussView, self).get_buttons()
        buttons.extend([
            PrimarySubmit(
                'examiner_add_public_comment',
                _('Add comment'),
                css_class='btn btn-default')
        ])
        return buttons

    def __send_comment_email(self, comment):
        comment_email.bulk_send_comment_email_to_students_and_examiners(
            comment_id=comment.id,
            domain_url_start=self.request.build_absolute_uri('/'))

    def save_object(self, form, commit=False):
        comment = super(ExaminerPublicDiscussView, self).save_object(form=form)
        comment.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EVERYONE
        comment.published_datetime = timezone.now()
        # self.__send_comment_email(comment=comment)
        return super(ExaminerPublicDiscussView, self).save_object(form=form, commit=True)

    def perform_after_save(self, comment):
        self.__send_comment_email(comment=comment)

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appurl(viewname='public-discuss')


class ExaminerWithAdminsDiscussView(ExaminerBaseFeedbackFeedView):
    """
    View for discussing with other examiners on the group and admins.

    All comments posted here are only visible to examiners and admins with access to
    the group.
    """
    template_name = 'devilry_group/feedbackfeed_examiner/feedbackfeed_examiner_examiner_admin_discuss.django.html'

    def get_form_heading_text_template_name(self):
        return 'devilry_group/include/examiner_commentform_discuss_examiner_headingtext.django.html'

    def get_buttons(self):
        buttons = super(ExaminerWithAdminsDiscussView, self).get_buttons()
        buttons.extend([
            PrimarySubmit(
                'examiner_add_comment_for_examiners_and_admins',
                _('Add note'))
        ])
        return buttons

    def __send_email_to_examiners(self, comment):
        comment_email.bulk_send_comment_email_to_examiners(
            comment_id=comment.id,
            domain_url_start=self.request.build_absolute_uri('/'))

    def save_object(self, form, commit=False):
        comment = super(ExaminerWithAdminsDiscussView, self).save_object(form=form)
        comment.visibility = group_models.GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS
        comment.published_datetime = timezone.now()
        return super(ExaminerWithAdminsDiscussView, self).save_object(form=form, commit=True)

    def perform_after_save(self, comment):
        self.__send_email_to_examiners(comment=comment)

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appurl(viewname='examiner-admin-discuss')


class EditGradeForm(forms.ModelForm):
    class Meta:
        model = group_models.FeedbackSet
        fields = [
            'grading_points',
        ]

    def __init__(self, *args, **kwargs):
        self.feedbackset = kwargs.get('instance')
        super(EditGradeForm, self).__init__(*args, **kwargs)


class EditGradePointsForm(EditGradeForm):
    def __init__(self, *args, **kwargs):
        super(EditGradePointsForm, self).__init__(*args, **kwargs)
        self.fields['grading_points'] = forms.IntegerField(
            min_value=0,
            max_value=self.feedbackset.group.parentnode.max_points,
            initial=self.feedbackset.grading_points)
        self.fields['grading_points'].label = ugettext_lazy('Grading')
        self.fields['grading_points'].help_text = \
            ugettext_lazy(
                'Give a score between {} to {} where {} is the minimum amount of points needed to pass.'.format(
                    0,
                    self.feedbackset.group.parentnode.max_points,
                    self.feedbackset.group.parentnode.passing_grade_min_points))


class EditGradePassedFailedForm(EditGradeForm):
    def __init__(self, *args, **kwargs):
        feedbackset = kwargs.get('instance')
        kwargs.update(initial={
            'grading_points': self.get_points_to_select_value(feedbackset)
        })
        super(EditGradePassedFailedForm, self).__init__(*args, **kwargs)
        self.fields['grading_points'] = forms.ChoiceField(
            choices=(('Passed', 'Passed'), ('Failed', 'Failed')),
            label=pgettext_lazy('grading', 'Passed?'),
            help_text=pgettext_lazy('grading', 'Check to provide a passing grade.'),
            required=True,
            initial=''
        )
        self.fields['grading_points'].label = ugettext_lazy('Grading')
        self.fields['grading_points'].help_text = ugettext_lazy('Check the box to give a passing grade')

    def get_points_to_select_value(self, feedbackset):
        assignment = feedbackset.group.parentnode
        current_grading_points = feedbackset.grading_points
        if current_grading_points >= assignment.passing_grade_min_points:
            return 'Passed'
        return 'Failed'

    def clean(self):
        super(EditGradePassedFailedForm, self).clean()
        grading_points = self.cleaned_data['grading_points']
        if grading_points == 'Passed':
            self.cleaned_data['grading_points'] = self.feedbackset.group.parentnode.max_points
        else:
            self.cleaned_data['grading_points'] = 0


class ExaminerEditGradeView(update.UpdateView):
    template_name = 'devilry_group/feedbackfeed_examiner/feedbackfeed_examiner_edit_grade.django.html'
    model = group_models.FeedbackSet

    def dispatch(self, request, *args, **kwargs):
        group = self.request.cradmin_role
        self.feedbackset = group_models.FeedbackSet.objects.get(group=group, id=kwargs.get('pk'))
        if group.cached_data.last_feedbackset != self.feedbackset or \
                not group.cached_data.last_published_feedbackset_is_last_feedbackset:
            raise Http404()
        return super(ExaminerEditGradeView, self).dispatch(request, *args, **kwargs)

    def get_pagetitle(self):
        return ugettext_lazy('Edit grade')

    def get_queryset_for_role(self, role):
        return group_models.FeedbackSet.objects.filter(group=role)

    def get_form_class(self):
        group = self.request.cradmin_role
        if group.parentnode.grading_system_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_POINTS:
            return EditGradePointsForm
        if group.parentnode.grading_system_plugin_id == core_models.Assignment.GRADING_SYSTEM_PLUGIN_ID_PASSEDFAILED:
            return EditGradePassedFailedForm

    def set_automatic_attributes(self, obj):
        obj.last_updated_by = self.request.user

    def save_object(self, form, commit=True):
        feedback_set = super(ExaminerEditGradeView, self).save_object(form=form, commit=True)
        feedback_email.send_feedback_edited_email(
            feedback_set=feedback_set, points=feedback_set.grading_points,
            domain_url_start=self.request.build_absolute_uri('/')
        )
        return feedback_set

    def get_field_layout(self):
        return [
            layout.Div(
                layout.Field('grading_points', focusonme='focusonme', css_class='form-control'),
                css_class='cradmin-globalfields'
            )
        ]

    def _get_assignment(self):
        return Assignment.objects\
            .filter(id=self.feedbackset.group.assignment.id)\
            .prefetch_point_to_grade_map()\
            .get()

    def get_context_data(self, **kwargs):
        context_data = super(ExaminerEditGradeView, self).get_context_data(**kwargs)
        context_data['feedbackset'] = self.feedbackset
        context_data['devilryrole'] = 'examiner'
        context_data['assignment'] = self._get_assignment()
        return context_data


class GroupCommentEditDeleteMixin(object):
    """
    Basic mixin/super-class for GroupCommentDeleteView and GroupCommentEditView.
    """
    model = group_models.GroupComment

    class Meta:
        abstract = True

    def get_queryset_for_role(self, role):
        """
        Filter out :obj:`devilry.devilry_group.models.GroupComment` based on the role of role of the
        crinstance and the primarykey of the comment since in this case only a single comment should be fetched.

        Args:
            role (GroupComment): The roleclass for the crinstance.

        Returns:
            QuerySet: QuerySet containing a single :class:`devilry.devilry_group.models.GroupComment`.
        """
        return group_models.GroupComment.objects.filter(
                feedback_set__group=role,
                user=self.request.user,
                id=self.kwargs.get('pk'))


class GroupCommentDeleteView(GroupCommentEditDeleteMixin, delete.DeleteView):
    """
    View for deleting an existing groupcomment with visibility set to private.
    When a groupcomment has visibility set to private, this means it's a feedbackdraft.
    """
    template_name = 'devilry_group/feedbackfeed_examiner/feedbackfeed_examiner_delete_groupcomment.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Checks if the GroupComment id passed is for a drafted comment.
        If the comment is not a draft, PermissionDenied is raised.

        Args:
            request (HttpRequest): request object.

        Returns:
            HttpResponseRedirect: Reponse redirect object.

        Raises:
            PermissionDenied: If comment is not a draft, this exception is raised.
        """
        if len(self.get_queryset_for_role(request.cradmin_role)) == 0:
            raise PermissionDenied
        return super(GroupCommentDeleteView, self).dispatch(request, *args, **kwargs)

    def get_object_preview(self):
        return ugettext_lazy('Groupcomment')

    def get_queryset_for_role(self, role):
        return group_models.GroupComment.objects.filter(
            feedback_set__group=role,
            id=self.kwargs.get('pk')).exclude_comment_is_not_draft_from_user(self.request.user)

    def get_success_url(self):
        return self.request.cradmin_app.reverse_appindexurl()


class GroupCommentEditView(EditGroupCommentBase):
    """
    """


class ExaminerFeedbackfeedRedirectView(View):
    def dispatch(self, request, *args, **kwargs):
        group = self.request.cradmin_role

        # if the last feedbackset of the group is not graded and the deadline has passed,
        # redirect to feedback view.
        if not group.cached_data.last_feedbackset.grading_published_datetime \
                and group.cached_data.last_feedbackset.deadline_datetime < timezone.now():
            return redirect(self.request.cradmin_app.reverse_appurl(viewname='feedback'))
        return redirect(self.request.cradmin_app.reverse_appurl(viewname='public-discuss'))


class App(crapp.App):
    appurls = [
        crapp.Url(
            r'^$',
            ExaminerFeedbackfeedRedirectView.as_view(),
            name=crapp.INDEXVIEW_NAME),
        crapp.Url(
            r'^feedback$',
            ensure_csrf_cookie(ExaminerFeedbackView.as_view()),
            name='feedback'),
        crapp.Url(
            r'^public-discuss',
            ExaminerPublicDiscussView.as_view(),
            name='public-discuss'
        ),
        crapp.Url(
            r'^examiner-admin-discuss',
            ExaminerWithAdminsDiscussView.as_view(),
            name='examiner-admin-discuss'
        ),
        crapp.Url(
            r'^edit/(?P<pk>\d+)$',
            ExaminerEditGradeView.as_view(),
            name='edit'
        ),
        crapp.Url(
            r'^groupcomment-delete/(?P<pk>\d+)$',
            GroupCommentDeleteView.as_view(),
            name="groupcomment-delete"),
        crapp.Url(
            r'^groupcomment-edit/(?P<pk>\d+)$',
            GroupCommentEditView.as_view(),
            name='groupcomment-edit'),
    ]
