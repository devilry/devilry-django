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

    def __init__(self, devilryrole):
        self.devilryrole = devilryrole
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
        if event_dict['type'] == 'comment':
            return GroupCommentItemValue(value=event_dict['obj'], devilryrole=self.devilryrole)
        else:
            return listbuilder.base.ItemValueRenderer(value=event_dict)

    def get_extra_css_classes_list(self):
        css_classes_list = super(TimelineListBuilderList, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-feed')
        return css_classes_list


class GroupCommentItemValue(listbuilder.base.ItemValueRenderer):
    """

    """
    valuealias = 'group_comment'
    template_name = 'devilry_group/listbuilder/base_groupcomment_item_value.django.html'

    @property
    def devilryrole(self):
        """

        Returns:

        """
        return self.kwargs['devilryrole']

    def get_extra_css_classes_list(self):
        """

        Returns:

        """
        css_classes_list = super(GroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-comment')
        if self.group_comment.user_role == comment_models.Comment.USER_ROLE_STUDENT:
            css_classes_list.append('devilry-group-feedbackfeed-comment-student')
        elif self.group_comment.user_role == comment_models.Comment.USER_ROLE_EXAMINER:
            css_classes_list.append('devilry-group-feedbackfeed-comment-examiner')
        elif self.group_comment.user_role == comment_models.Comment.USER_ROLE_ADMIN:
            css_classes_list.append('devilry-group-feedbackfeed-comment-admin')
        return css_classes_list
