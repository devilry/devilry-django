# -*- coding: utf-8 -*-


# Devilry imports
from devilry.devilry_comment.models import CommentFile
from devilry.devilry_group.feedbackfeed_builder import builder_base
from devilry.devilry_group import models as group_models


class FeedbackFeedSidebarBuilder(builder_base.FeedbackFeedBuilderBase):
    def __init__(self, **kwargs):
        super(FeedbackFeedSidebarBuilder, self).__init__(**kwargs)
        self.feedbackset_dict = {}

    def __get_files_for_comment(self, comment):
        commentfiles = comment.commentfile_set.all()
        commentfilelist = []
        for commentfile in commentfiles:
            commentfilelist.append(commentfile)
        return commentfilelist

    def build(self):
        for feedbackset in self.feedbacksets:
            self.feedbackset_dict[feedbackset.created_datetime] = {
                'feedbackset_num': 0,
                'feedbackset': feedbackset
            }
        self.feedbackset_dict = self.sort_dict(self.feedbackset_dict)

    def get_as_list(self):
        feedbackset_list = []
        num = 1
        for key_datetime in sorted(self.feedbackset_dict.keys()):
            feedbacksets = self.feedbackset_dict[key_datetime]
            feedbacksets['feedbackset_num'] = num
            feedbackset_list.append(feedbacksets)
            num += 1
        return feedbackset_list
