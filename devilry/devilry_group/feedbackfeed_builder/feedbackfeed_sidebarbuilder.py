# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Devilry imports
from devilry.devilry_group.feedbackfeed_builder import builder_base
from devilry.devilry_group import models as group_models


class FeedbackFeedSidebarBuilder(builder_base.FeedbackFeedBuilderBase):
    """Builds a sorted structure for uploaded files for :class:`~devilry.devilry_group.models.FeedbackSet`s.

    The dictionary with one FeedbackSet, one GroupComment with two CommentFiles produced looks like this::
        {
            # feedbackset created date
            01.01.2016 09:00:
                {
                    # feedbackset content
                    'feedbackset_num': 1,
                    'feedbackset': :obj:`~devilry.devilry_group.models.FeedbackSet`,
                    'comments':
                        {
                            # comment published date
                            01.02.2016 03:00:
                                {
                                    'groupcomment': :obj:`~devilry.devilry_group.models.GroupComment`,
                                    'files': [
                                        :obj:`~devilry.devilry_comment.models.CommentFile`,
                                        :obj:`~devilry.devilry_comment.models.CommentFile`
                                    ]
                                }
                        }
                }
            ...
        }
    """
    def __init__(self, **kwargs):
        """__init__ takes a :class:`~devilry.devilry_group.models.FeedbackSet`.

        Args:
            feedbacksets (QuerySet): prefetched feedbacksets, groupcomments, and commentfiles.
        """
        super(FeedbackFeedSidebarBuilder, self).__init__(**kwargs)
        self.feedbackset_dict = {}

    def __get_files_for_comment(self, comment):
        """Get all files for ``comment``, and add them to a list.

        Args:
            comment (GroupComment): Get :obj:`~devilry.devilry_comment.models.CommentFile`s for.

        Returns:
            List: A list of files or None.
        """
        commentfiles = comment.commentfile_set.all()
        commentfilelist = []
        for commentfile in commentfiles:
            commentfilelist.append(commentfile)
        return commentfilelist

    # def __get_comments_for_feedbackset(self, feedbackset):
    #     """Get all :class:`~devilry.devilry_group.GroupComment`s for ``feedbackset`
    #
    #     Args:
    #         feedbackset (FeedbackSet): Get :obj:`~devilry.devilry_group.models.GroupComment` objects for.
    #
    #     Returns:
    #         dict: Sorted dictionary of :class:`~devilry.devilry_group.GroupComment`s.
    #     """
    #     group_comments = feedbackset.groupcomment_set.all()
    #     group_comment_dict = {}
    #     for group_comment in group_comments:
    #         comment_files = self.__get_files_for_comment(comment=group_comment)
    #         if comment_files:
    #             group_comment_dict[group_comment.published_datetime] = {
    #                 'group_comment': group_comment,
    #                 'files': comment_files
    #             }
    #             if group_comment.user_role == group_models.GroupComment.USER_ROLE_STUDENT:
    #                 group_comment_dict[group_comment.published_datetime]['candidate'] = self._get_candidate_from_user(
    #                     user=group_comment.user)
    #             elif group_comment.user_role == group_models.GroupComment.USER_ROLE_EXAMINER:
    #                 group_comment_dict[group_comment.published_datetime]['examiner'] = self._get_examiner_from_user(
    #                     user=group_comment.user)
    #     if len(group_comment_dict) > 0:
    #         group_comment_dict = self.sort_dict(group_comment_dict)
    #     return group_comment_dict

    def build(self):
        """
        Build a dictionary with a list of all files for each feedbackset and sorts it.
        """
        for feedbackset in self.feedbacksets:
            # commentdict = self.__get_comments_for_feedbackset(feedbackset=feedbackset)
            self.feedbackset_dict[feedbackset.created_datetime] = {
                'feedbackset_num': 0,
                'feedbackset': feedbackset,
                # 'comments': commentdict
            }
        self.feedbackset_dict = self.sort_dict(self.feedbackset_dict)

    def get_as_list(self):
        """
        Get a flat list of dictionaries from sorted filedict.
        The elements are added to the list in ascending order based on the FeedbackSets
        chronological order(created_datetime).

        ``feedbackset_dict`` can be accessed directly through a instance of this class, but this function provides lists
        of dictionaries representing the elements.

        The above example with one FeedbackSet, one GroupComment with two CommentFiles as a list structure::
        [
            {
                'feedbackset_num': 1,
                'feedbackset': :obj:`~devilry.devilry_group.models.FeedbackSet`,
                'comments':
                    [
                        {
                            'groupcomment': :obj:`~devilry.devilry_group.models.GroupComment`,
                            'files': [
                                :obj:`~devilry.devilry_comment.models.CommentFile`,
                                :obj:`~devilry.devilry_comment.models.CommentFile`
                            ]
                        }
                        ...
                    ]
            }
            ...
        ]

        Returns:
            list: List of dictionaries.
        """
        feedbackset_list = []
        num = 1
        for key_datetime in sorted(self.feedbackset_dict.keys()):
            feedbacksets = self.feedbackset_dict[key_datetime]
            feedbacksets['feedbackset_num'] = num

            # Create list of comments.
            # commentlist = []
            # for commentkey in sorted(feedbacksets['comments'].keys()):
            #     commentdict = feedbacksets['comments'][commentkey]
            #     commentlist.append(commentdict)
            # feedbacksets['comments'] = commentlist
            feedbackset_list.append(feedbacksets)
            num += 1
        return feedbackset_list
