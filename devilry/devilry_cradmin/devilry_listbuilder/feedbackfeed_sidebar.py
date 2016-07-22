# Devilry/cradmin imports
from django_cradmin.viewhelpers import listbuilder


class SidebarListBuilderList(listbuilder.base.List):
    """Builds an overview of CommentFiles for each GroupComment and the FeedbackSet they belong to.
    """
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
        self.append(renderable=FeedbackSetItemValue(value=feedbackset_dict['feedbackset_num']))
        valuerenderer = GroupCommentDateTimeListBuilderList.from_groupcomments(
                comment_list=feedbackset_dict['comments'])
        self.append(renderable=valuerenderer)

    def get_extra_css_classes_list(self):
        css_classes_list = super(SidebarListBuilderList, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-sidebar-filecontent')
        return css_classes_list


class GroupCommentDateTimeListBuilderList(listbuilder.base.List):
    """Builds a list over :class:`~devilry.devilry_comment.models.CommentFile`s.

    Builds a list of CommentFiles for all :obj:`~devilry.devilry_group.GroupComment`s
    that belong to a FeedbackSet. See :class:`~FileListBuilder`.
    """
    @classmethod
    def from_groupcomments(cls, comment_list, **kwargs):
        """Builds a list of :obj:`~devilry.devilry_group.models.GroupComment`s.

        Args:
            comment_list (list): List of GroupComment dictionaries.

        Returns:
            List: Instance of CrAdmins renderable List.
        """
        commentdatebuilder_list = cls(**kwargs)
        for comment_dict in comment_list:
            commentdatebuilder_list.append_dict(comment_dict=comment_dict)
        return commentdatebuilder_list

    def append_dict(self, comment_dict):
        """Appends renderables to this list.

        Appends the ``published_date`` of a GroupComment and adds a list of CommentFiles for that GroupComment.
        See :class:`~GroupCommentDateTimeItemValue` and :class:`~FileListBuilderList`.

        Args:
            comment_dict (dict): Dictionary for a GroupComment.
        """
        self.append(renderable=GroupCommentDateTimeItemValue(value=comment_dict['groupcomment']))
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

    Attributes:
        valuealias (int): A FeedbackSets chronological order.
    """
    valuealias = 'feedbackset_num'
    template_name = 'devilry_group/listbuilder_sidebar/sidebar_feedbackset_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(FeedbackSetItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-sidebar-deadlines')
        return css_classes_list


class GroupCommentDateTimeItemValue(listbuilder.base.ItemValueRenderer):
    """Renderable for a GroupComment.

    Attributes:
        valuealias (:obj:`~devilry.devilry_group.models.GroupComment`): Instance.
    """
    valuealias = 'groupcomment'
    template_name = 'devilry_group/listbuilder_sidebar/sidebar_comment_date_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(GroupCommentDateTimeItemValue, self).get_extra_css_classes_list()
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
        css_classes_list.append('devilry-group-feedbackfeed-sidebar-files')
        return css_classes_list
