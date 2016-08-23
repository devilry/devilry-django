# Devilry/cradmin imports
from django_cradmin.viewhelpers import listbuilder
from devilry.devilry_comment import models as comment_models


class TimelineListBuilderList(listbuilder.base.List):
    """A list of all events for a feedbackfeed.

    The list is built from a pre-built timeline, and all events
    are added as renderables in the list.
    """

    @classmethod
    def from_built_timeline(cls, built_timeline, **kwargs):
        """Creates a instance of TimelineListBuilderList.

        Appends events from `built_timeline`.

        Args:
            built_timeline: The built and sorted feedbackfeed timeline

        Returns:
            TimelineListBuilderList: listbuilder instance.
        """
        listbuilder_list = cls(**kwargs)
        for event_dict in built_timeline.get_as_list():
            listbuilder_list.append_eventdict(event_dict)
        return listbuilder_list

    def __init__(self, devilryrole, group, assignment):
        self.devilryrole = devilryrole
        self.group = group
        self.assignment = assignment
        super(TimelineListBuilderList, self).__init__()

    def append_eventdict(self, event_dict):
        """Appends a ValueRenderer instance to the list.

        Args:
            event_dict: Event metadata dictionary.
        """
        valuerenderer = self.__get_item_value(event_dict=event_dict)
        self.append(renderable=valuerenderer)

    def __get_item_value(self, event_dict):
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
                                                    user_obj=event_dict.get('candidate'),
                                                    assignment=self.assignment)
            elif group_comment.user_role == comment_models.Comment.USER_ROLE_EXAMINER:
                return ExaminerGroupCommentItemValue(value=group_comment,
                                                     devilry_viewrole=self.devilryrole,
                                                     user_obj=event_dict.get('examiner'),
                                                     assignment=self.assignment)
            elif group_comment.user_role == comment_models.Comment.USER_ROLE_ADMIN:
                return AdminGroupCommentItemValue(value=group_comment,
                                                  devilry_viewrole=self.devilryrole,
                                                  assignment=self.assignment)
        elif event_dict['type'] == 'deadline_created':
            return DeadlineCreatedItemValue(value=event_dict['feedbackset'], devilryrole=self.devilryrole)
        elif event_dict['type'] == 'deadline_expired':
            return DeadlineExpiredItemValue(value=event_dict['deadline_datetime'], devilryrole=self.devilryrole)
        elif event_dict['type'] == 'grade':
            return GradeItemValue(value=event_dict['feedbackset'], devilryrole=self.devilryrole, group=self.group)

    def get_extra_css_classes_list(self):
        css_classes_list = super(TimelineListBuilderList, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-feed')
        return css_classes_list


class BaseItemValue(listbuilder.base.ItemValueRenderer):
    """Base class for all items in the list.
    """
    @property
    def devilry_viewrole(self):
        """
        Get the devilry role for the view.

        Returns:
             str: 'student', 'examiner' or a admin role.
        """
        return self.kwargs['devilry_viewrole']


class BaseEventItemValue(BaseItemValue):
    """Base class for all events.

    Superclass for all events that occur in the timeline such as ``deadline created``, ``deadline expired``,
    ``grading passed`` and ``grading failed``.
    """

    def get_timeline_datetime(self):
        """
        Get the timeline datetime for the event.

        Returns:
             DateTime: The event datetime

        Raises:
            NotImplementedError: if not implemented.
        """
        raise NotImplementedError('Must be implemented by subclass')


class BaseGroupCommentItemValue(BaseItemValue):
    """Base class for a GroupComment item.

    Superclass for the different types of comments(student-comment, examiner-comment and admin-comment).
    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder_feedbackfeed/base_groupcomment_item_value.django.html'

    def __init__(self, *args, **kwargs):
        super(BaseGroupCommentItemValue, self).__init__(*args, **kwargs)
        self.user_obj = kwargs.get('user_obj')
        self.assignment = kwargs.get('assignment')

    def get_extra_css_classes_list(self):
        css_classes_list = super(BaseGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment')
        return css_classes_list


class StudentGroupCommentItemValue(BaseGroupCommentItemValue):
    """Student :class:`~devilry.devilry_group.models.GroupComment`.
    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder_feedbackfeed/student_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(StudentGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-student')
        return css_classes_list


class ExaminerGroupCommentItemValue(BaseGroupCommentItemValue):
    """Examiner :class:`~devilry.devilry_group.models.GroupComment`.
    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder_feedbackfeed/examiner_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(ExaminerGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-examiner')
        return css_classes_list


class AdminGroupCommentItemValue(BaseGroupCommentItemValue):
    """Admin :class:`~devilry.devilry_group.models.GroupComment`.
    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder_feedbackfeed/admin_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(AdminGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-admin')
        return css_classes_list


class DeadlineCreatedItemValue(BaseEventItemValue):
    """Deadline created event.
    """
    valuealias = 'feedbackset'
    template_name = 'devilry_group/listbuilder_feedbackfeed/deadline_created_item_value.django.html'

    def get_timeline_datetime(self):
        return self.value.created_datetime

    def get_extra_css_classes_list(self):
        css_classes_list = super(DeadlineCreatedItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message-deadline-created')
        return css_classes_list


class DeadlineExpiredItemValue(BaseEventItemValue):
    """Deadline expired event
    """
    valuealias = 'deadline_datetime'
    template_name = 'devilry_group/listbuilder_feedbackfeed/deadline_expired_item_value.django.html'

    def get_timeline_datetime(self):
        return self.value

    def get_extra_css_classes_list(self):
        css_classes_list = super(DeadlineExpiredItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message-deadline-expired')
        return css_classes_list


class GradeItemValue(BaseEventItemValue):
    """Grading event.
    """
    valuealias = 'feedbackset'
    template_name = 'devilry_group/listbuilder_feedbackfeed/grading_item_value.django.html'

    @property
    def group(self):
        return self.kwargs['group']

    def get_timeline_datetime(self):
        return self.value.grading_published_datetime

    def get_extra_css_classes_list(self):
        css_classes_list = super(GradeItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message-grade')
        return css_classes_list
