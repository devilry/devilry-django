# Ignore line length in this file
# flake8: noqa: E501
import logging
from ievv_opensource.ievv_customsql import customsql_registry

from devilry.apps.core.models import Period
from devilry.devilry_dbcache.models import AssignmentGroupCachedData

log = logging.getLogger(__name__)


class AssignmentGroupDbCacheCustomSql(customsql_registry.AbstractCustomSql):

    def initialize(self):
        self.execute_sql_from_files([
            'feedbackset/helperfunctions.sql',
            'commentfile/helperfunctions.sql',
            'assignment_group/helperfunctions.sql',
            'assignment_group/triggers.sql',
            # 'feedbackset/validate.sql',
            'feedbackset/triggers.sql',
            'groupcomment/triggers.sql',
            'imageannotationcomment/triggers.sql',
            'commentfile/triggers.sql',
            'assignment_group_cached_data/rebuild.sql',
        ])

    def recreate_data(self):
        from devilry.apps.core.models import AssignmentGroup
        from devilry.devilry_group.models import FeedbackSet, ImageAnnotationComment, GroupComment
        from devilry.devilry_comment.models import CommentFile

        log.info("Rebuilding AssignmentGroup cached data")
        log.info("AssignmentGroup count: %s" % AssignmentGroup.objects.count())
        log.info("FeedbackSet count: %s" % FeedbackSet.objects.count())
        log.info("GroupComments count: %s" % GroupComment.objects.count())
        log.info("ImageAnnotationComment count: %s" % ImageAnnotationComment.objects.count())
        log.info("CommentFile count: %s" % CommentFile.objects.count())

        AssignmentGroupCachedData.objects.all().delete()
        for period in Period.objects.order_by('-start_time').iterator():
            self.execute_sql("""
                SELECT devilry__rebuild_assignmentgroupcacheddata_for_period({period_id});
            """.format(period_id=period.id))

