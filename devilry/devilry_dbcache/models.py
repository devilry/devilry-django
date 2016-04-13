from django.db import models

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet


class AssignmentGroupCachedData(models.Model):
    # NOTE: We may need to reverse this relationship (a cached_data field on AssignmentGroup)
    group = models.OneToOneField(AssignmentGroup, related_name='cached_data')
    first_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                          null=True, blank=True)
    last_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                         null=True, blank=True)
    last_published_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                                   null=True, blank=True)

    # TODO: Add comment count fields
    # TODO: Add feedbackset count field
