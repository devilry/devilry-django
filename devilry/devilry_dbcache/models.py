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

    feedbackset_count = models.PositiveIntegerField()

    public_total_comment_count = models.PositiveIntegerField()
    public_student_comment_count = models.PositiveIntegerField()
    public_examiner_comment_count = models.PositiveIntegerField()
    public_admin_comment_count = models.PositiveIntegerField()

    public_total_imageannotationcomment_count = models.PositiveIntegerField()
    public_student_imageannotationcomment_count = models.PositiveIntegerField()
    public_examiner_imageannotationcomment_count = models.PositiveIntegerField()
    public_admin_imageannotationcomment_count = models.PositiveIntegerField()

    file_upload_count_total = models.PositiveIntegerField()
    file_upload_count_student = models.PositiveIntegerField()
    file_upload_count_examiner = models.PositiveIntegerField()
