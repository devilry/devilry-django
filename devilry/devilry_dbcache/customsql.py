# Ignore line length in this file
# flake8: noqa: E501
import logging
from ievv_opensource.ievv_customsql import customsql_registry

from devilry.apps.core.models import Period
from devilry.devilry_dbcache.models import AssignmentGroupCachedData

log = logging.getLogger(__name__)


class AssignmentGroupDbCacheCustomSql(customsql_registry.AbstractCustomSql):

    _initialize_sqlfiles = [
        'general_purpose_functions.sql',
        'feedbackset/helperfunctions.sql',
        'commentfile/helperfunctions.sql',
        'assignment_group/triggers.sql',
        'feedbackset/validate.sql',
        'feedbackset/triggers.sql',
        'groupcomment/triggers.sql',
        'imageannotationcomment/triggers.sql',
        'comment/triggers.sql',
        'commentfile/triggers.sql',
        'examiner/triggers.sql',
        'candidate/triggers.sql',
        'assignment_group_cached_data/rebuild.sql',
        'assignment/triggers.sql'
    ]

    def initialize(self):
        self.execute_sql_from_files(self._initialize_sqlfiles)

    def recreate_data(self):
        from devilry.apps.core.models import AssignmentGroup, Candidate, Examiner
        from devilry.devilry_group.models import FeedbackSet, ImageAnnotationComment, GroupComment
        from devilry.devilry_comment.models import CommentFile

        log.info("Rebuilding AssignmentGroup cached data")
        log.info("AssignmentGroup count: %s" % AssignmentGroup.objects.count())
        log.info("FeedbackSet count: %s" % FeedbackSet.objects.count())
        log.info("GroupComments count: %s" % GroupComment.objects.count())
        log.info("ImageAnnotationComment count: %s" % ImageAnnotationComment.objects.count())
        log.info("CommentFile count: %s" % CommentFile.objects.count())
        log.info("Examiner count: %s" % Examiner.objects.count())
        log.info("Candidate count: %s" % Candidate.objects.count())

        AssignmentGroupCachedData.objects.all().delete()
        for period in Period.objects.order_by('-start_time').iterator():
            self.execute_sql("""
                SELECT devilry__rebuild_assignmentgroupcacheddata_for_period({period_id});
            """.format(period_id=period.id))

    def clear(self):
        drop_statements = self.make_drop_statements_from_sql_files(self._initialize_sqlfiles)
        self.execute_sql_multiple(reversed(drop_statements))
        self._delete_generated_objects()

    def _delete_generated_objects(self):
        self.execute_sql("""
            DELETE FROM devilry_dbcache_assignmentgroupcacheddata;
        """)
