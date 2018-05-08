# Devilry/cradmin imports
from django_cradmin.viewhelpers import listbuilder
from devilry.devilry_group import models as group_models


class SidebarListBuilderList(listbuilder.base.List):
    """Builds an overview of CommentFiles for each GroupComment and the FeedbackSet they belong to.
    """
    template_name = 'devilry_group/listbuilder_sidebar/sidebar_list.django.html'

    @classmethod
    def from_built_sidebar(cls, built_sidebar, **kwargs):
        """Creates a instance of this class and builds a renderable list from a dictionary.

        ``built_sidebar`` is the dictionary structure the list is created from.
        See :class:`~devilry.devilry_group.feedbackfeed_builder.feedbackfeed_sidebarbuilder.FeedbackFeedSidebarBuilder`

        Args:
            built_sidebar (FeedbackFeedSidebarBuilder): Instance of sidebar structure.

        Returns:
            List: Instance of CrAdmins renderable List.
        """
        listbuilder_list = cls(**kwargs)
        for feedbackset_files_dict in built_sidebar.get_as_list():
            listbuilder_list.append_dict(feedbackset_files_dict)
        return listbuilder_list

    def __init__(self, devilryrole, group, assignment):
        self.devilryrole = devilryrole
        self.group = group
        self.assignment = assignment
        super(SidebarListBuilderList, self).__init__()

    def append_dict(self, feedbackset_dict):
        """Appends renderables to this list.

        For each :class:`~devilry.devilry_group.models.FeedbackSet` its chronological number is added a as
        renderable item and a List for comments added. See :class:`~GroupCommentDateTimeListBuilder`.

        Args:
            feedbackset_dict (dict): Dictionary containing FeedbackSet data.
        """
        self.append(renderable=FeedbackSetItemValue(value=feedbackset_dict['feedbackset'],
                                                    feedbackset_num=feedbackset_dict['feedbackset_num']))

    def get_base_css_classes_list(self):
        return ['devilry-group-feedbackfeed-buttonbar__list']


class GroupCommentListBuilderList(listbuilder.base.List):
    """Builds a list over :class:`~devilry.devilry_comment.models.CommentFile`s.

    Builds a list of CommentFiles for all :obj:`~devilry.devilry_group.GroupComment`s
    that belong to a FeedbackSet. See :class:`~FileListBuilder`.
    """
    @classmethod
    def from_groupcomments(cls, comment_list, assignment, devilryrole, **kwargs):
        """Builds a list of :obj:`~devilry.devilry_group.models.GroupComment`s.

        Args:
            comment_list (List): List of GroupComment dictionaries.
            assignment (:class:`~.devilry.apps.core.models.assignment.Assignment`): The assignment.
            devilryrole (str): The viewrole for the user.

        Returns:
            List: Instance of CrAdmins renderable List.
        """
        groupcommentbuilder_list = cls(**kwargs)
        for comment_dict in comment_list:
            groupcommentbuilder_list.append_dict(assignment=assignment, comment_dict=comment_dict, devilryrole=devilryrole)
        return groupcommentbuilder_list

    def append_dict(self, assignment, comment_dict, devilryrole):
        """Appends renderables to this list.

        Appends the ``published_date`` of a GroupComment and adds a list of CommentFiles for that GroupComment.
        See :class:`~GroupCommentDateTimeItemValue` and :class:`~FileListBuilderList`.

        Args:
            assignment (:class:`~.devilry.apps.core.models.assignment.Assignment`):
            comment_dict (dict): Dictionary of ``GroupComment``s and ``CommentFile``s.
            devilryrole (str): The viewrole for the user.

        Args:
            comment_dict (dict): Dictionary for a GroupComment.
        """
        group_comment = comment_dict.get('group_comment')
        user_obj = None
        if group_comment.user_role == group_models.GroupComment.USER_ROLE_STUDENT:
            user_obj = comment_dict.get('candidate')
        elif group_comment.user_role == group_models.GroupComment.USER_ROLE_EXAMINER:
            user_obj = comment_dict.get('examiner')
        self.append(renderable=GroupCommentItemValue(
            value=group_comment,
            user_obj=user_obj,
            devilryrole=devilryrole,
            assignment=assignment))
        valuerenderer = FileListBuilderList.from_files(comment_dict['files'])
        self.append(renderable=valuerenderer)


class FileListBuilderList(listbuilder.base.List):
    """
    Building a list of files for a FeedbackSet.
    """
    @classmethod
    def from_files(cls, file_list, **kwargs):
        """Builds a list of :obj:`~devilry.devilry_comment.models.CommentFile`s.

        Args:
            file_list (list): List of CommentFiles

        Returns:
            List: Instance of CrAdmins renderable List.
        """
        filebuilder_list = cls(**kwargs)
        for commentfile in file_list:
            filebuilder_list.append(FileItemValue(value=commentfile))
        return filebuilder_list


class FeedbackSetItemValue(listbuilder.base.ItemValueRenderer):
    """Renderable for a FeedbackSet.
    """
    valuealias = 'feedbackset'
    template_name = 'devilry_group/listbuilder_sidebar/sidebar_feedbackset_item_value.django.html'

    def __init__(self, value, feedbackset_num=None):
        super(FeedbackSetItemValue, self).__init__(value=value)
        self.feedbackset_num = feedbackset_num

    def get_extra_css_classes_list(self):
        css_classes_list = super(FeedbackSetItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-buttonbar-deadlines')
        return css_classes_list


class GroupCommentItemValue(listbuilder.base.ItemValueRenderer):
    """Renderable for a GroupComment.
    """
    valuealias = 'groupcomment'
    template_name = 'devilry_group/listbuilder_sidebar/sidebar_comment_item_value.django.html'

    def __init__(self, *args, **kwargs):
        super(GroupCommentItemValue, self).__init__(*args, **kwargs)
        self.user_obj = kwargs.get('user_obj')
        self.assignment = kwargs.get('assignment')
        self.devilryrole = kwargs.get('devilryrole')

    def get_extra_css_classes_list(self):
        css_classes_list = super(GroupCommentItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-buttonbar-groupcomment')
        return css_classes_list


class FileItemValue(listbuilder.base.ItemValueRenderer):
    """Renderable for a CommentFile.

    Attributes:
        valuealias (:obj:`~devilry.devilry_comment.models.CommentFile`): Instance.
    """
    valuealias = 'delivery_file'
    template_name = 'devilry_group/listbuilder_sidebar/sidebar_file_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(FileItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-buttonbar-files')
        return css_classes_list
