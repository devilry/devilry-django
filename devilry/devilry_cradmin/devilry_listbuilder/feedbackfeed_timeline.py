# Devilry/cradmin imports
from django.conf import settings
from django_cradmin.viewhelpers import listbuilder

from devilry.apps.core.group_user_lookup import GroupUserLookup
from devilry.devilry_comment import models as comment_models
from devilry.devilry_group.models import GroupComment, FeedbackSet, GroupCommentEditHistory
from devilry.utils import datetimeutils


class TimeLineListBuilderList(listbuilder.base.List):

    @classmethod
    def from_built_timeline(cls, built_timeline, **kwargs):
        listbuilder_list = cls()
        attempt_num = 1
        for feedback_set_num, feedbackset_event in enumerate(built_timeline.get_as_list()):
            feedbackset = feedbackset_event['feedbackset']
            if not feedbackset.is_merge_type \
               and feedbackset.feedbackset_type != FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT:
                attempt_num += 1
            listbuilder_list.append(
                FeedbackSetTimelineListBuilderList.from_built_timeline(
                    built_timeline=feedbackset_event['feedbackset_events'],
                    feedbackset=feedbackset_event['feedbackset'],
                    attempt_num=attempt_num,
                    **kwargs)
            )
        return listbuilder_list

    def get_extra_css_classes_list(self):
        css_classes_list = super(TimeLineListBuilderList, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-feed')
        return css_classes_list


class FeedbackSetTimelineListBuilderList(listbuilder.base.List):
    """
    A list of all events for a specific :obj:`~devilry.devilry_group.models.FeedbackSet`.
    """

    @classmethod
    def from_built_timeline(cls, built_timeline, feedbackset, attempt_num, **kwargs):
        """Creates a instance of TimelineListBuilderList.

        Appends events from `built_timeline`.

        Args:
            built_timeline: The built and sorted feedbackfeed timeline
            feedbackset: The :class:`~.devilry.devilry_group.models.FeedbackSet` the events belong to.
            attempt_num: The chronological number of the feedbackset.

        Returns:
            TimelineListBuilderList: listbuilder instance.
        """
        listbuilder_list = cls(feedbackset, **kwargs)
        listbuilder_list.append(renderable=FeedbackSetCreatedItemValue(value=feedbackset,
                                                                       attempt_num=attempt_num,
                                                                       assignment=kwargs.get('assignment'),
                                                                       devilry_viewrole=kwargs.get('devilryrole')))
        item_values_list = []
        for event_dict in built_timeline:
            item_values_list.append(listbuilder_list.get_item_value(event_dict=event_dict))
        listbuilder_list.renderable_list.append(
            FeedbackSetContentList(feedbackset=feedbackset, renderables_list=item_values_list)
        )
        return listbuilder_list

    def __init__(self, feedbackset, group, assignment, requestuser, devilryrole):
        self.feedbackset = feedbackset
        self.assignment = assignment
        self.requestuser = requestuser
        self.devilryrole = devilryrole
        self.group = group
        self.group_user_lookup = GroupUserLookup(
            group=group,
            assignment=assignment,
            requestuser=requestuser,
            requestuser_devilryrole=devilryrole)
        super(FeedbackSetTimelineListBuilderList, self).__init__()

    def get_item_value(self, event_dict):
        """Creates a ItemValueRenderer based on the event type.

        If the event type is `comment`:
         -  create and return a StudentGroupCommentItemValue,
            ExaminerGroupCommentItemValue or AdminGroupCommentItemValue.

        If the event type is `deadline_created`:
         -  create and return a DeadlineCreatedItemValue.

        If the event type is `deadline_expired`:
         -  create and return a DeadlineExpiredItemValue.

        If the event type is `grade`:
         -  create and return a DeadlineExpiredItemValue.

        Args:
            event_dict: Event metadata dictionary.

        Returns:
            BaseItemValue: Subclass of BaseItemValue.
        """
        if event_dict['type'] == 'comment':
            group_comment = event_dict['obj']
            if group_comment.user_role == comment_models.Comment.USER_ROLE_STUDENT:
                return StudentGroupCommentItemValue(value=group_comment,
                                                    devilry_viewrole=self.devilryrole,
                                                    assignment=self.assignment,
                                                    requestuser=self.requestuser,
                                                    group_user_lookup=self.group_user_lookup)
            elif group_comment.user_role == comment_models.Comment.USER_ROLE_EXAMINER:
                return ExaminerGroupCommentItemValue(value=group_comment,
                                                     devilry_viewrole=self.devilryrole,
                                                     assignment=self.assignment,
                                                     requestuser=self.requestuser,
                                                     group_user_lookup=self.group_user_lookup)
            elif group_comment.user_role == comment_models.Comment.USER_ROLE_ADMIN:
                return AdminGroupCommentItemValue(value=group_comment,
                                                  devilry_viewrole=self.devilryrole,
                                                  assignment=self.assignment,
                                                  requestuser=self.requestuser,
                                                  group_user_lookup=self.group_user_lookup)
        elif event_dict['type'] == 'deadline_expired':
            return DeadlineExpiredItemValue(value=event_dict['deadline_datetime'], devilry_viewrole=self.devilryrole,
                                            feedbackset=event_dict['feedbackset'], group=self.group)
        elif event_dict['type'] == 'grade':
            return GradeItemValue(value=event_dict['feedbackset'], assignment=self.assignment,
                                  devilry_viewrole=self.devilryrole, grade_points=event_dict['grade_points'],
                                  group=self.group)
        elif event_dict['type'] == 'deadline_moved':
            return DeadlineMovedItemValue(value=event_dict['obj'], is_last=event_dict['is_last'],
                                          devilry_viewrole=self.devilryrole, feedbackset=event_dict['feedbackset'],
                                          group=self.group)
        elif event_dict['type'] == 'grading_updated':
            return GradingUpdatedItemValue(value=event_dict['obj'], devilry_viewrole=self.devilryrole,
                                           assignment=self.assignment, feedbackset=event_dict['feedbackset'],
                                           next_grading_points=event_dict['next_grading_points'], group=self.group)

    def get_extra_css_classes_list(self):
        css_classes_list = super(FeedbackSetTimelineListBuilderList, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-feed__feedbackset-wrapper')
        return css_classes_list


class FeedbackSetContentList(listbuilder.base.List):
    """
    Simply adds a css wrapper-class for all events that belong to a feedbackset.
    """
    def __init__(self, feedbackset, renderables_list):
        self.feedbackset = feedbackset
        super(FeedbackSetContentList, self).__init__()
        for renderable in renderables_list:
            self.renderable_list.append(renderable)

    def get_extra_css_classes_list(self):
        css_classes_list = super(FeedbackSetContentList, self).get_extra_css_classes_list()
        if self.feedbackset.is_merge_type:
            css_classes_list.append('devilry-group-feedbackfeed-feed__feedbackset-wrapper__content-merge-type')
        else:
            css_classes_list.append('devilry-group-feedbackfeed-feed__feedbackset-wrapper--content')
        return css_classes_list


class BaseItemValue(listbuilder.base.ItemValueRenderer):
    """
    Base class for all items in the list.
    """
    def __init__(self, *args, **kwargs):
        self.devilryrole = kwargs.get('devilry_viewrole')
        super(BaseItemValue, self).__init__(*args, **kwargs)

    @property
    def devilry_viewrole(self):
        """
        Get the devilry role for the view.

        Returns:
             str: 'student', 'examiner' or a admin role.
        """
        return self.devilryrole

    def get_extra_css_classes_list(self):
        css_classes_list = super(BaseItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-itemvalue')
        return css_classes_list


class BaseEventItemValue(BaseItemValue):
    """
    Base class for all events.

    Superclass for all events that occur in the timeline such as ``deadline created``, ``deadline expired``,
    ``grading passed`` and ``grading failed``.
    """

    @property
    def group(self):
        return self.kwargs['group']

    def get_timeline_datetime(self):
        """
        Get the timeline datetime for the event.

        Returns:
             DateTime: The event datetime

        Raises:
            NotImplementedError: if not implemented.
        """
        raise NotImplementedError('Must be implemented by subclass')

    def get_base_css_classes_list(self):
        return ['devilry-group-feedbackfeed-event-message']

    @property
    def changed_by_user_id(self):
        """
        ID of the user that made the change.

        This must be implemented in each subclass as this dependent on the model-obj set as self.value.

        Returns:
            int: A user ID.
        """
        raise NotImplementedError()

    @property
    def show_changed_by_user(self):
        """
        If the user should be rendered, based on the the role of the requestuser and
        if the assignment is anonymized.

        Returns:
            bool: True
        """
        if self.changed_by_user_id is None:
            return False
        assignment = self.group.parentnode
        if not assignment.is_anonymous:
            return True

        # Handle anonymous assignment
        # TODO: When we add ANONYMIZATIONMODE_FULLY_ANONYMOUS, we need something more here
        return self.devilry_viewrole not in ('student', 'examiner', 'periodadmin')


class FeedbackSetCreatedItemValue(BaseItemValue):
    template_name = 'devilry_group/listbuilder_feedbackfeed/feedbackset_info_item_value.django.html'
    valuealias = 'feedbackset'

    def __init__(self, attempt_num, assignment, *args, **kwargs):
        self.attempt_num = attempt_num
        self.assignment = assignment
        super(FeedbackSetCreatedItemValue, self).__init__(*args, **kwargs)

    @property
    def deadline_as_string(self):
        return datetimeutils.datetime_to_url_string(self.value.deadline_datetime)

    def get_timeline_datetime(self):
        return self.value.created_datetime

    def is_graded(self):
        return self.value.grading_published_datetime is not None

    def get_extra_css_classes_list(self):
        css_classes_list = super(FeedbackSetCreatedItemValue, self).get_extra_css_classes_list()
        if self.value.feedbackset_type == FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT:
            css_classes_list.append('devilry-group-feedbackfeed-feed__feedbackset-wrapper--header-first-attempt')
        else:
            css_classes_list.append('devilry-group-feedbackfeed-feed__feedbackset-wrapper--header')
        return css_classes_list


class BaseGroupCommentItemValue(BaseItemValue):
    """
    Base class for a GroupComment item.

    Superclass for the different types of comments(student-comment, examiner-comment and admin-comment).
    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder_feedbackfeed/base_groupcomment_item_value.django.html'

    def __init__(self, requestuser, *args, **kwargs):
        super(BaseGroupCommentItemValue, self).__init__(*args, **kwargs)
        self.assignment = kwargs.get('assignment')
        self.group_user_lookup = kwargs.get('group_user_lookup')
        self.requestuser = requestuser

    def get_display_name_for_comment_user(self):
        raise NotImplementedError()

    def _should_add_with_badge_css_class(self):
        return (
            self.group_comment.part_of_grading or
            self.group_comment.visibility == GroupComment.VISIBILITY_VISIBLE_TO_EXAMINER_AND_ADMINS)

    def get_display_name_html(self):
        return self.group_user_lookup.get_long_name_from_user(
            user=self.group_comment.user,
            user_role=self.group_comment.user_role, html=True
        )

    def include_edit_links(self):
        """
        Render links for editing `GroupComment`.
        """
        return self.group_comment.user_can_edit_comment(user=self.requestuser)

    def include_badge(self):
        """
        Include right-hand-badge with comment-info in `GroupComment`.
        """
        return True

    def include_published_last_edited_datetime(self):
        """
        Include the last published datetime, or edited datetime if edited, in
        `GroupComment`.
        """
        return True

    def include_files(self):
        """
        Render uploaded files for a `GroupComment`.
        """
        return True

    def is_published(self):
        return self.group_comment.get_published_datetime() != None

    def get_last_edited_datetime_history(self):
        if hasattr(self.group_comment, 'last_edithistory_datetime'):
            return self.group_comment.last_edithistory_datetime
        return None

    def get_extra_css_classes_list(self):
        css_classes_list = super(BaseGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment')
        return css_classes_list


class StudentGroupCommentItemValue(BaseGroupCommentItemValue):
    """
    Student :class:`~devilry.devilry_group.models.GroupComment`.
    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder_feedbackfeed/student_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(StudentGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-student')
        if self.group_comment.feedback_set.current_deadline():
            if self.group_comment.published_datetime > self.group_comment.feedback_set.current_deadline():
                css_classes_list.append('devilry-group-feedbackfeed-comment--with-badge')
        return css_classes_list


class StudentGroupCommentItemValueMinimal(BaseGroupCommentItemValue):
    """
    Student :class:`~devilry.devilry_group.models.GroupComment` minimal renderable.

    Only shows the publish datetime, user, and text. Files and badges are excluded
    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder_feedbackfeed/student_groupcomment_item_value.django.html'

    def include_edit_links(self):
        return False

    def include_badge(self):
        return False

    def include_published_last_edited_datetime(self):
        return False

    def include_files(self):
        return False

    def get_extra_css_classes_list(self):
        css_classes_list = super(StudentGroupCommentItemValueMinimal, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-student')
        css_classes_list.append('devilry-group-feedbackfeed-comment-student--minimal')
        return css_classes_list


class ExaminerGroupCommentItemValue(BaseGroupCommentItemValue):
    """
    Examiner :class:`~devilry.devilry_group.models.GroupComment`.
    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder_feedbackfeed/examiner_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(ExaminerGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-examiner')
        if self._should_add_with_badge_css_class():
            css_classes_list.append('devilry-group-feedbackfeed-comment--with-badge')
        return css_classes_list


class ExaminerGroupCommentItemValueMinimal(BaseGroupCommentItemValue):
    def include_edit_links(self):
        return False

    def include_badge(self):
        return False

    def include_published_last_edited_datetime(self):
        return False

    def include_files(self):
        return False

    def get_extra_css_classes_list(self):
        css_classes_list = super(ExaminerGroupCommentItemValueMinimal, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-examiner')
        css_classes_list.append('devilry-group-feedbackfeed-comment-examiner--minimal')
        return css_classes_list


class AdminGroupCommentItemValue(BaseGroupCommentItemValue):
    """
    Admin :class:`~devilry.devilry_group.models.GroupComment`.
    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder_feedbackfeed/admin_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(AdminGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-admin')
        if self._should_add_with_badge_css_class():
            css_classes_list.append('devilry-group-feedbackfeed-comment--with-badge')
        return css_classes_list


class AdminGroupCommentItemValueMinimal(BaseGroupCommentItemValue):
    def include_edit_links(self):
        return False

    def include_badge(self):
        return False

    def include_published_last_edited_datetime(self):
        return False

    def include_files(self):
        return False

    def get_extra_css_classes_list(self):
        css_classes_list = super(AdminGroupCommentItemValueMinimal, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-admin')
        css_classes_list.append('devilry-group-feedbackfeed-comment-admin--minimal')
        return css_classes_list


class AbstractDeadlineEventItemValue(BaseEventItemValue):
    """
    Abstract class for deadline events.
    """
    valuealias = 'deadline_datetime'

    def __init__(self, *args, **kwargs):
        self.feedbackset = kwargs.pop('feedbackset')
        super(AbstractDeadlineEventItemValue, self).__init__(*args, **kwargs)

    @property
    def deadline_as_string(self):
        return datetimeutils.datetime_to_url_string(self.feedbackset.deadline_datetime)

    def get_timeline_datetime(self):
        return self.value


class DeadlineMovedItemValue(AbstractDeadlineEventItemValue):
    """
    Deadline moved event.
    """
    valuealias = 'feedbackset_history_obj'
    template_name = 'devilry_group/listbuilder_feedbackfeed/deadline_moved_item_value.django.html'

    def __init__(self, is_last=False, *args, **kwargs):
        self.is_last = is_last
        super(DeadlineMovedItemValue, self).__init__(*args, **kwargs)

    def get_timeline_datetime(self):
        return self.value.changed_datetime

    @property
    def changed_by_user_id(self):
        return self.feedbackset_history_obj.changed_by_id

    def get_extra_css_classes_list(self):
        css_classes_list = super(DeadlineMovedItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message__deadline-moved')
        return css_classes_list


class DeadlineExpiredItemValue(AbstractDeadlineEventItemValue):
    """
    Deadline expired event.
    """
    valuealias = 'deadline_datetime'
    template_name = 'devilry_group/listbuilder_feedbackfeed/deadline_expired_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(DeadlineExpiredItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message__deadline-expired')
        return css_classes_list


class GradeItemValue(BaseEventItemValue):
    """
    Grading event.
    """
    valuealias = 'feedbackset'
    template_name = 'devilry_group/listbuilder_feedbackfeed/grading_item_value.django.html'

    def __init__(self, *args, **kwargs):
        self.assignment = kwargs['assignment']
        self.grade_points = kwargs['grade_points']
        super(GradeItemValue, self).__init__(*args, **kwargs)

    @property
    def group(self):
        return self.kwargs['group']

    @property
    def changed_by_user_id(self):
        return self.feedbackset.grading_published_by_id

    @property
    def deadline_as_string(self):
        return datetimeutils.datetime_to_url_string(self.feedbackset.deadline_datetime)

    def get_timeline_datetime(self):
        return self.value.grading_published_datetime

    def get_extra_css_classes_list(self):
        css_classes_list = super(GradeItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message__grade')
        return css_classes_list


class GradingUpdatedItemValue(BaseEventItemValue):
    valuealias = 'grading_updated'
    template_name = 'devilry_group/listbuilder_feedbackfeed/grading_updated_item_value.django.html'

    def __init__(self, *args, **kwargs):
        self.assignment = kwargs['assignment']
        self.feedbackset = kwargs['feedbackset']
        self.next_grading_points = kwargs['next_grading_points']
        super(GradingUpdatedItemValue, self).__init__(*args, **kwargs)

    @property
    def group(self):
        return self.kwargs['group']

    @property
    def changed_by_user_id(self):
        return self.grading_updated.updated_by_id

    def get_timeline_datetime(self):
        return self.value.updated_datetime

    def get_extra_css_classes_list(self):
        css_classes_list = super(GradingUpdatedItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message__grade')
        return css_classes_list
