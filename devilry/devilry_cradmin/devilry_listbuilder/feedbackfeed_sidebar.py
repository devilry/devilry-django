# Devilry/cradmin imports
from django_cradmin.viewhelpers import listbuilder


class SidebarListBuilderList(listbuilder.base.List):
    """
    Building a list of FeedbackSets
    """
    @classmethod
    def from_built_sidebar(cls, built_sidebar, **kwargs):
        """

        Args:
            built_sidebar:
            **kwargs:

        Returns:

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
        """

        Args:
            feedbackset_files_dict:

        Returns:

        """
        self.append(renderable=FeedbackSetItemValue(value=feedbackset_dict['feedbackset_num']))
        # valuerenderer = FileListBuilderList.from_files(files=feedbackset_dict['files'])
        # self.append(renderable=valuerenderer)
        valuerenderer = GroupCommentDateTimeListBuilderList.from_groupcomments(comment_dict=feedbackset_dict['comments'])
        self.append(renderable=valuerenderer)

    def get_extra_css_classes_list(self):
        css_classes_list = super(SidebarListBuilderList, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-sidebar-filecontent')
        return css_classes_list


class GroupCommentDateTimeListBuilderList(listbuilder.base.List):
    """

    """
    @classmethod
    def from_groupcomments(cls, comment_dict, **kwargs):
        """

        Args:
            comment_dict:
            **kwargs:

        Returns:

        """
        commentdatebuilder_list = cls(**kwargs)
        for comment_date in comment_dict:
            commentdatebuilder_list.append_dict(comment_date=comment_date, comment_dict=comment_dict)
        return commentdatebuilder_list

    def append_dict(self, comment_date, comment_dict):
        """

        Args:
            comment_date:
            comment_dict:

        Returns:

        """
        self.append(renderable=GroupCommentDateTimeItemValue(value=comment_date))
        valuerenderer = FileListBuilderList.from_files(comment_dict[comment_date]['files'])
        self.append(renderable=valuerenderer)


class FileListBuilderList(listbuilder.base.List):
    """
    Building a list of files for a FeedbackSet.
    """

    @classmethod
    def from_files(cls, files, **kwargs):
        """

        Args:
            files:
            **kwargs:

        Returns:

        """
        filebuilder_list = cls(**kwargs)
        print files
        for commentfile in files:
            if commentfile is not None:
                filebuilder_list.append(FileItemValue(value=commentfile))
        return filebuilder_list


class FeedbackSetItemValue(listbuilder.base.ItemValueRenderer):
    """

    """
    valuealias = 'feedbackset_num'
    template_name = 'devilry_group/listbuilder_sidebar/sidebar_feedbackset_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(FeedbackSetItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-sidebar-deadlines')
        return css_classes_list


class GroupCommentDateTimeItemValue(listbuilder.base.ItemValueRenderer):
    """

    """
    valuealias = 'groupcomment_datetime'
    template_name = 'devilry_group/listbuilder_sidebar/sidebar_comment_date_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(GroupCommentDateTimeItemValue, self).get_extra_css_classes_list()
        return css_classes_list


class FileItemValue(listbuilder.base.ItemValueRenderer):
    """
    Class for a CommentFile item.
    """
    valuealias = 'delivery_file'
    template_name = 'devilry_group/listbuilder_sidebar/sidebar_file_item_value.django.html'

    def get_extra_css_classes_list(self):
        css_classes_list = super(FileItemValue, self).get_extra_css_classes_list()
        css_classes_list.append('devilry-group-feedbackfeed-sidebar-files')
        return css_classes_list
