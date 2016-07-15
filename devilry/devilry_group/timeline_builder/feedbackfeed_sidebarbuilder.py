# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports
import collections
import datetime

# Devilry imports
from devilry.devilry_group.timeline_builder import builder_base


class FeedbackFeedSidebarBuilder(builder_base.FeedbackFeedBuilderBase):
    """
    Builds a sorted structure over files for FeedbackSet.
    Creates a dictionary sorted over the :obj:`~devilry.devilry_group.models.FeedbackSet.created_datetime`.

    The dictionary produced looks like this::
        {
            datetime_object:
                {
                    'feedbackset_num': some number based on the feedbacksets chronological order,
                    'feedbackset': a feedbackset instance,
                    'files': a list of files for this feedbackset
                }
            ...
        }
    """
    def __init__(self, feedbacksets):
        """
        Creates a list of dictionaries containing FeedbackSet as key and a list of CommentFiles as value.

        Args:
            feedbackset_queryset: prefetched feedbacksets, groupcomments, and commentfiles.
        """
        super(FeedbackFeedSidebarBuilder, self).__init__()
        self.feedbacksets = list(feedbacksets)
        self.file_dict = {}

    def __get_files_for_feedbackset(self, feedbackset):
        """
        Get all files for ``feedbackset``, and add them to a list.

        Args:
            feedbackset (FeedbackSet): Get files for.

        Returns:
            List: A list of files or None.
        """
        comments = feedbackset.groupcomment_set.all()
        if len(comments) == 0:
            return None
        files = []
        for comment in comments:
            for commentfile in comment.commentfile_set.all():
                files.append(commentfile)
        return files

    def build(self):
        """
        Build a dictionary with a list of all files for each feedbackset and sorts it.
        """
        for feedbackset in self.feedbacksets:
            filelist = self.__get_files_for_feedbackset(feedbackset=feedbackset)
            if filelist:
                # Skip if no files.
                self.file_dict[feedbackset.created_datetime] = {
                    'feedbackset_num': 0,
                    'feedbackset': feedbackset,
                    'files': filelist
                }
        self.file_dict = self.sort_dict(self.file_dict)

    def get_as_list(self):
        """
        Get a flat list of dictionaries from sorted filedict.
        The elements are added to the list in ascending order based on the FeedbackSets chronological order.

        ``file_dict`` can be accessed directly through a instance of this class, but this function provides a
        simple interface over all FeedbackSets' files.

        Returns:
            List: List of dictionaries.
        """
        filelist = []
        num = 1
        for key_datetime in sorted(self.file_dict.keys()):
            files = self.file_dict[key_datetime]
            files['feedbackset_num'] = num
            filelist.append(files)
            num += 1
        return filelist
