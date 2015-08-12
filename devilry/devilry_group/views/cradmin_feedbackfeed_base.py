import datetime
from crispy_forms.layout import Submit
from django_cradmin.acemarkdown.widgets import AceMarkdownWidget
from devilry.devilry_group import models
from django_cradmin.viewhelpers import create
import collections
from devilry.devilry_group.models import GroupComment
from django.utils.translation import ugettext_lazy as _
from crispy_forms import layout
from devilry.devilry_markup import parse_markdown


class FeedbackFeedBaseView(create.CreateView):
    template_name = "devilry_group/feedbackfeed.django.html"

    # for cradmin CreateView
    model=GroupComment
    fields=["text"]

    def _get_comments_for_group(self, group):
        raise NotImplementedError("Subclasses must implement _get_queryset_for_group!")

    def _get_feedbacksets_for_group(self, group):
        return models.FeedbackSet.objects.filter(group=group)

    def __add_comments_to_timeline(self, group, timeline):
        comments = self._get_comments_for_group(group)
        for comment in comments:
            if comment.published_datetime not in timeline.keys():
                timeline[comment.published_datetime] = []
            timeline[comment.published_datetime].append({
                "type": "comment",
                "obj": comment
            })
        return timeline

    def __add_announcements_to_timeline(self, feedbacksets, timeline):
        if len(feedbacksets) == 0:
            return timeline
        first_feedbackset = feedbacksets[0]
        last_deadline = first_feedbackset.deadline_datetime
        for feedbackset in feedbacksets[0:]:
            if feedbackset.deadline_datetime not in timeline.keys():
                timeline[feedbackset.deadline_datetime] = []
            timeline[feedbackset.deadline_datetime].append({
                "type": "deadline_expired"
            })
            if feedbackset.created_datetime not in timeline.keys():
                timeline[feedbackset.created_datetime] = []

            if feedbackset.deadline_datetime < first_feedbackset.deadline_datetime:
                timeline[feedbackset.created_datetime].append({
                    "type": "deadline_created",
                    "obj": first_feedbackset.deadline_datetime,
                    "user": first_feedbackset.created_by
                })
                first_feedbackset = feedbackset
            elif feedbackset is not feedbacksets[0]:
                timeline[feedbackset.created_datetime].append({
                    "type": "deadline_created",
                    "obj": feedbackset.deadline_datetime,
                    "user": feedbackset.created_by
                })
            if feedbackset.deadline_datetime > last_deadline:
                last_deadline = feedbackset.deadline_datetime

            if feedbackset.published_datetime is not None:
                if feedbackset.published_datetime not in timeline.keys():
                    timeline[feedbackset.published_datetime] = []
                timeline[feedbackset.published_datetime].append({
                    "type": "grade",
                    "obj": feedbackset.points
                })
        return last_deadline, timeline

    def __sort_timeline(self, timeline):
        sorted_timeline = collections.OrderedDict(sorted(timeline.items()))
        return sorted_timeline

    def __build_timeline(self, group, feedbacksets):
        timeline = {}
        timeline = self.__add_comments_to_timeline(group, timeline)
        last_deadline, timeline = self.__add_announcements_to_timeline(feedbacksets, timeline)
        timeline = self.__sort_timeline(timeline)

        return last_deadline, timeline

    def get_context_data(self, **kwargs):
        context = super(FeedbackFeedBaseView, self).get_context_data(**kwargs)
        context['subject'] = self.request.cradmin_role.assignment.period.subject
        context['assignment'] = self.request.cradmin_role.assignment
        context['period'] = self.request.cradmin_role.assignment.period

        feedbacksets = self._get_feedbacksets_for_group(self.request.cradmin_role)
        context['last_deadline'], context['timeline'] = self.__build_timeline(self.request.cradmin_role, feedbacksets)
        context['feedbacksets'] = feedbacksets
        context['last_feedbackset'] = feedbacksets[0]
        context['current_date'] = datetime.datetime.now()

        return context

    submit_use_label = _('Post comment')

    def get_form_css_classes(self):
        """
        Returns list of css classes set on the form. You normally
        want to override :meth:`.get_extra_form_css_classes` instead
        of this method unless you want to provide completely custom
        form styles.
        """
        form_css_classes = [
        ]
        return form_css_classes

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
        app = self.request.cradmin_app
        user = self.request.user
        if self.request.cradmin_role.is_candidate(user):
            return [Submit('student_add_comment',
                           'Add comment',
                           css_class='btn btn-success')]
        elif self.request.cradmin_role.is_examiner(user):
            return [Submit('examiner_add_comment_for_examiners',
                           'Add comment for examiners',
                           css_class='btn btn-primary'),
                    Submit('examiner_add_public_comment',
                           'Add public comment',
                           css_class='btn btn-primary'),
                    Submit('examiner_add_comment_to_feedback_draft',
                           'Add comment to feedback draft',
                           css_class='btn btn-primary')
                    ]

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
                        layout.HTML('<p>Drag and drop, or click <a href="#"><strong>here</strong></a> to upload files</p>'),
                        css_class='panel-footer'
                    ),
                    css_class='panel panel-default'
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
        # form.fields['text'].widget = WysiHtmlTextArea(attrs={})
        form.fields['text'].widget = AceMarkdownWidget()
        form.fields['text'].label = False
        return form

    def save_object(self, form, commit=True):
        print '\nsave object from form\n'

        assignment_group = self.request.cradmin_role
        user = self.request.user
        time = datetime.datetime.now()

        object = form.save(commit=False)
        object.user = user
        object.comment_type = 'groupcomment'
        object.feedback_set = assignment_group.feedbackset_set.latest('created_datetime')

        if assignment_group.is_candidate(user):
            object.user_role = 'student'
            object.instant_publish = True
            object.visible_for_students = True
            object.published_datetime = time
        elif assignment_group.is_examiner(user):
            object.user_role = 'examiner'
            print 'is examiner'

            if form.data.get('examiner_add_comment_for_examiners'):
                print 'examiner_add_comment_for_examiners'
                object.instant_publish = True
                object.visible_for_students = False
            elif form.data.get('examiner_add_public_comment'):
                print 'examiner_add_public_comment'
                object.instant_publish = True
                object.visible_for_students = True
            elif form.data.get('examiner_add_comment_to_feedback_draft'):
                print 'examiner_add_comment_to_feedback_draft'
                object.instant_publish = False
                object.visible_for_students = False
                object.published_datetime = time
        else:
            object.user_role = 'admin'
            object.instant_publish = True
            object.visible_for_students = True

        if commit:
            object.save()
        return object
