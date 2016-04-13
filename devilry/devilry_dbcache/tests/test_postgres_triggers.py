from django import test
from django.db import connection
from model_mommy import mommy

from devilry.devilry_dbcache.models import AssignmentGroupCachedData


class Test(test.TestCase):
    def __run_sql(self, sql):
        # schema_editor.connection.ops.prepare_sql_script(sql)
        cursor = connection.cursor()
        cursor.execute(sql)

    def setUp(self):
        # self.__run_sql("""
        #     DROP FUNCTION IF EXISTS devilry_dbcache_on_feedbackset_update();
        #     DROP TRIGGER IF EXISTS devilry_dbcache_on_feedbackset_update_trigger ON devilry_dbcache_feedbackset;
        # """)
        #       IF NEW.grading_published_datetime is NULL
        #         NEW.grading_published_datetime
        self.__run_sql("""
            CREATE OR REPLACE FUNCTION devilry_dbcache_on_feedbackset_insert_or_update() RETURNS TRIGGER AS
            $$
            BEGIN
                -- TODO: Handle that the new feedbackset is older than the last!
                IF EXISTS (SELECT 1 FROM devilry_dbcache_assignmentgroupcacheddata WHERE group_id = NEW.group_id) THEN
                    -- If the AssignmentGroupCachedData for feedbackset.group does exist, update it
                    IF NEW.grading_published_datetime IS NULL THEN
                        UPDATE devilry_dbcache_assignmentgroupcacheddata
                            SET
                                last_feedbackset_id = NEW.id;
                    ELSE
                        UPDATE devilry_dbcache_assignmentgroupcacheddata
                            SET
                                last_feedbackset_id = NEW.id,
                                last_published_feedbackset_id = NEW.id;
                    END IF;
                ELSE
                    -- If the AssignmentGroupCachedData for feedbackset.group does NOT exist, create it
                    IF NEW.grading_published_datetime IS NULL THEN
                        INSERT INTO devilry_dbcache_assignmentgroupcacheddata
                            (group_id, last_feedbackset_id, last_published_feedbackset_id)
                        VALUES (NEW.group_id, NEW.id, NULL);
                    ELSE
                        INSERT INTO devilry_dbcache_assignmentgroupcacheddata
                            (group_id, last_feedbackset_id, last_published_feedbackset_id)
                        VALUES (NEW.group_id, NEW.id, NEW.id);
                    END IF;
                END IF;
                RETURN NEW;
            END
            $$
            LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS devilry_dbcache_on_feedbackset_insert_or_update_trigger
                ON devilry_group_feedbackset;
            CREATE TRIGGER devilry_dbcache_on_feedbackset_insert_or_update_trigger
                AFTER INSERT OR UPDATE ON devilry_group_feedbackset
                FOR EACH ROW
                    EXECUTE PROCEDURE devilry_dbcache_on_feedbackset_insert_or_update();
        """)

    def test_something(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet')
        cached_data = AssignmentGroupCachedData.objects.get(group=feedbackset.group)
        self.assertEqual(feedbackset, cached_data.last_feedbackset)

        # feedbackset.save()
