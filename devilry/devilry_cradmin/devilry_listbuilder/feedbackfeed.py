# Devilry/cradmin imports
from django_cradmin.viewhelpers import listbuilder

from devilry.devilry_comment import models as comment_models


class TimelineListBuilderList(listbuilder.base.List):
    """

    """
    @classmethod
    def from_built_timeline(cls, built_timeline, **kwargs):
        """

        Args:
            built_timeline:
            **kwargs:

        Returns:

        """
        listbuilder_list = cls(**kwargs)
        for event_dict in built_timeline.get_as_list():
            listbuilder_list.append_eventdict(event_dict)
        return listbuilder_list

    def __init__(self, devilryrole, group):
        self.devilryrole = devilryrole
        self.group = group
        super(TimelineListBuilderList, self).__init__()

    def append_eventdict(self, event_dict):
        """

        Args:
            built_timeline:

        Returns:

        """
        valuerenderer = self.__get_item_value(event_dict=event_dict)
        self.append(renderable=valuerenderer)

    def __get_item_value(self, event_dict):
        """

        Args:
            event_dict:

        Returns:

        """
        if event_dict['type'] == 'comment':
            group_comment = event_dict['obj']
            if group_comment.user_role == comment_models.Comment.USER_ROLE_STUDENT:
                return StudentGroupCommentItemValue(value=group_comment, devilryrole=self.devilryrole)
            elif group_comment.user_role == comment_models.Comment.USER_ROLE_EXAMINER:
                return ExaminerGroupCommentItemValue(value=group_comment, devilryrole=self.devilryrole)
            elif group_comment.user_role == comment_models.Comment.USER_ROLE_ADMIN:
                return AdminGroupCommentItemValue(value=group_comment, devilryrole=self.devilryrole)
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
    """

    """
    @property
    def devilryrole(self):
        """

        Returns:

        """
        return self.kwargs['devilryrole']


class BaseEventItemValue(BaseItemValue):
    """

    """
    def get_timeline_datetime(self):
        """

        Returns:

        """
        raise NotImplementedError('Must be implemented')


class BaseGroupCommentItemValue(BaseItemValue):
    """

    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder/base_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        """

        Returns:

        """
        css_classes_list = super(BaseGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment')
        return css_classes_list


class StudentGroupCommentItemValue(BaseGroupCommentItemValue):
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder/student_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        """
        """
        css_classes_list = super(StudentGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-student')
        return css_classes_list


class ExaminerGroupCommentItemValue(BaseGroupCommentItemValue):
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder/examiner_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        """
        """
        css_classes_list = super(ExaminerGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-examiner')
        return css_classes_list


class AdminGroupCommentItemValue(BaseGroupCommentItemValue):
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder/admin_groupcomment_item_value.django.html'

    def get_extra_css_classes_list(self):
        """
        """
        css_classes_list = super(AdminGroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment-admin')
        return css_classes_list


class DeadlineCreatedItemValue(BaseEventItemValue):
    """

    """
    valuealias = 'feedbackset'
    template_name = 'devilry_group/listbuilder/deadline_created_item_value.django.html'

    def get_timeline_datetime(self):
        return self.feedbackset.created_datetime

    def get_extra_css_classes_list(self):
        css_classes_list = super(DeadlineCreatedItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message-deadline-created')
        return css_classes_list


class DeadlineExpiredItemValue(BaseEventItemValue):
    """

    """
    valuealias = 'deadline_datetime'
    template_name = 'devilry_group/listbuilder/deadline_expired_item_value.django.html'

    def get_timeline_datetime(self):
        return self.deadline_datetime

    def get_extra_css_classes_list(self):
        css_classes_list = super(DeadlineExpiredItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message-deadline-expired')
        return css_classes_list


class GradeItemValue(BaseEventItemValue):
    valuealias = 'feedbackset'
    template_name = 'devilry_group/listbuilder/grading_item_value.django.html'

    @property
    def group(self):
        return self.kwargs['group']

    def get_timeline_datetime(self):
        return self.feedbackset.grading_published_datetime

    def get_extra_css_classes_list(self):
        css_classes_list = super(GradeItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-event-message-grade')
        return css_classes_list
