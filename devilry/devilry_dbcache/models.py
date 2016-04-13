from django.db import models

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_group.models import FeedbackSet


class AssignmentGroupCachedData(models.Model):
    # NOTE: We may need to reverse this relationship (a cached_data field on AssignmentGroup)
    group = models.OneToOneField(AssignmentGroup, related_name='cached_data')
    last_feedbackset = models.ForeignKey(FeedbackSet, related_name='+')
    last_published_feedbackset = models.ForeignKey(FeedbackSet, related_name='+',
                                                   null=True, blank=True)
