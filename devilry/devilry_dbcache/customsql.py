# Ignore line length in this file
# flake8: noqa: E501
import logging
from ievv_opensource.ievv_customsql import customsql_registry

log = logging.getLogger(__name__)


class AssignmentGroupDbCacheCustomSql(customsql_registry.AbstractCustomSql):

    def initialize(self):
        self.execute_sql_from_files([
            'all.sql'
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

        self.execute_sql("""
             DELETE FROM devilry_dbcache_assignmentgroupcacheddata;
             DO language plpgsql $$
             BEGIN
               PERFORM devilry_dbcache_rebuild_assignmentgroupcacheddata();
             END
             $$;
        """)
