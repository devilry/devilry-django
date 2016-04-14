from datetime import datetime, timedelta
from django import test
from django.conf import settings
from django.db import connection
from django.utils import timezone
from model_mommy import mommy

from devilry.apps.core.models import AssignmentGroup
from devilry.devilry_dbcache.models import AssignmentGroupCachedData
from devilry.devilry_group.models import FeedbackSet


def _run_sql(sql):
    cursor = connection.cursor()
    cursor.execute(sql)


def _remove_triggers():
    _run_sql("""
        DROP TRIGGER IF EXISTS devilry_dbcache_on_assignmentgroup_insert_trigger
            ON core_assignmentgroup;
        DROP TRIGGER IF EXISTS devilry_dbcache_on_feedbackset_insert_or_update_trigger
            ON devilry_group_feedbackset;
    """)


def _create_triggers():
    _run_sql("""

        CREATE OR REPLACE FUNCTION devilry_dbcache_timestampvalue_has_changed(
            param_old_value timestamp with time zone, param_new_value timestamp with time zone)
        RETURNS boolean AS $$
        BEGIN
            IF (param_old_value IS NULL AND param_new_value IS NOT NULL)
                OR (param_new_value IS NULL AND param_old_value IS NOT NULL)
                OR (param_new_value != param_old_value)
            THEN
                RETURN TRUE;
            ELSE
                RETURN FALSE;
            END IF;
        END
        $$ LANGUAGE plpgsql;


        CREATE OR REPLACE FUNCTION devilry_dbcache_find_last_published_feedbackset_id_in_group(param_group_id integer)
        RETURNS integer AS $$
        DECLARE
            var_last_published_feedbackset_id integer;
        BEGIN
            SELECT
                id INTO var_last_published_feedbackset_id
            FROM devilry_group_feedbackset
            WHERE group_id = param_group_id AND grading_published_datetime IS NOT NULL
            ORDER BY created_datetime DESC
            LIMIT 1;

            RETURN var_last_published_feedbackset_id;
        END
        $$ LANGUAGE plpgsql;


        CREATE OR REPLACE FUNCTION devilry_dbcache_find_first_feedbackset_id_in_group(param_group_id integer)
        RETURNS integer AS $$
        DECLARE
            var_first_feedbackset_id integer;
        BEGIN
            SELECT
                id INTO var_first_feedbackset_id
            FROM devilry_group_feedbackset
            WHERE group_id = param_group_id
            ORDER BY created_datetime ASC
            LIMIT 1;

            RETURN var_first_feedbackset_id;
        END
        $$ LANGUAGE plpgsql;

        CREATE OR REPLACE FUNCTION devilry_dbcache_find_last_feedbackset_id_in_group(param_group_id integer)
        RETURNS integer AS $$
        DECLARE
            var_last_feedbackset_id integer;
        BEGIN
            SELECT
                id INTO var_last_feedbackset_id
            FROM devilry_group_feedbackset
            WHERE group_id = param_group_id
            ORDER BY created_datetime DESC
            LIMIT 1;

            RETURN var_last_feedbackset_id;
        END
        $$ LANGUAGE plpgsql;


        CREATE OR REPLACE FUNCTION devilry_dbcache_on_feedbackset_insert_or_update() RETURNS TRIGGER AS $$
        DECLARE
            var_first_feedbackset_id integer;
            var_last_feedbackset_id integer;
            var_last_published_feedbackset_id integer;
            var_cached_data_exists boolean;
            var_cached_data record;
        BEGIN
            SELECT
               EXISTS (SELECT 1 FROM devilry_dbcache_assignmentgroupcacheddata WHERE group_id = NEW.group_id)
               INTO var_cached_data_exists;

            IF NOT var_cached_data_exists THEN
                -- If the AssignmentGroupCachedData for feedbackset.group does NOT exist, create it
                -- We assume that if this is the first time we create an AssignmentGroupCachedData
                -- for the group, this is the first FeedbackSet in the group!
                IF NEW.grading_published_datetime IS NOT NULL THEN
                    var_last_published_feedbackset_id := NEW.id;
                END IF;
                INSERT INTO devilry_dbcache_assignmentgroupcacheddata (
                    group_id,
                    first_feedbackset_id,
                    last_feedbackset_id,
                    last_published_feedbackset_id)
                VALUES (
                    NEW.group_id,
                    NEW.id,
                    NEW.id,
                    var_last_published_feedbackset_id);
            ELSE
                SELECT
                    cached_data.group_id AS group_id,
                    cached_data.first_feedbackset_id AS first_feedbackset_id,
                    cached_data.last_feedbackset_id AS last_feedbackset_id,
                    cached_data.last_published_feedbackset_id AS last_published_feedbackset_id,
                    first_feedbackset.created_datetime AS first_feedbackset_created_datetime,
                    last_feedbackset.created_datetime AS last_feedbackset_created_datetime,
                    last_published_feedbackset.created_datetime AS last_published_feedbackset_created_datetime
                FROM devilry_dbcache_assignmentgroupcacheddata AS cached_data
                LEFT JOIN devilry_group_feedbackset first_feedbackset
                    ON cached_data.first_feedbackset_id = first_feedbackset.id
                LEFT JOIN devilry_group_feedbackset last_feedbackset
                    ON cached_data.last_feedbackset_id = last_feedbackset.id
                LEFT JOIN devilry_group_feedbackset last_published_feedbackset
                    ON cached_data.last_published_feedbackset_id = last_published_feedbackset.id
                WHERE cached_data.group_id = NEW.group_id
                INTO var_cached_data;

                -- We only update the cache if any fields affecting the cache is changed
                IF NEW.created_datetime < var_cached_data.first_feedbackset_created_datetime THEN
                    var_first_feedbackset_id := NEW.id;
                ELSE
                    var_first_feedbackset_id := var_cached_data.first_feedbackset_id;
                END IF;

                IF NEW.created_datetime > var_cached_data.last_feedbackset_created_datetime THEN
                    var_last_feedbackset_id := NEW.id;
                ELSE
                    var_last_feedbackset_id := var_cached_data.last_feedbackset_id;
                END IF;

                IF (var_cached_data.last_published_feedbackset_id IS NULL
                    OR var_cached_data.last_published_feedbackset_id != NEW.id
                    ) AND NEW.grading_published_datetime IS NOT NULL
                    AND (
                        var_cached_data.last_published_feedbackset_created_datetime IS NULL
                        OR NEW.created_datetime > var_cached_data.last_published_feedbackset_created_datetime)
                THEN
                    var_last_published_feedbackset_id := NEW.id;
                ELSE
                    IF var_cached_data.last_published_feedbackset_id = NEW.id THEN
                        -- This happens if we unpublish the currently last published feedbackset.
                        -- We have to perform at SELECT query to find the correct value. This is a
                        -- bit expensive, but it is not a problem since this rarely happens, and
                        -- it will very rarely be done in bulk.
                        var_last_published_feedbackset_id := devilry_dbcache_find_last_published_feedbackset_id_in_group(NEW.group_id);
                    ELSE
                        var_last_published_feedbackset_id := var_cached_data.last_published_feedbackset_id;
                    END IF;
                END IF;

                UPDATE devilry_dbcache_assignmentgroupcacheddata
                SET
                    first_feedbackset_id = var_first_feedbackset_id,
                    last_feedbackset_id = var_last_feedbackset_id,
                    last_published_feedbackset_id = var_last_published_feedbackset_id
                WHERE group_id = NEW.group_id;
            END IF;

            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS devilry_dbcache_on_feedbackset_insert_or_update_trigger
            ON devilry_group_feedbackset;
        CREATE TRIGGER devilry_dbcache_on_feedbackset_insert_or_update_trigger
            AFTER INSERT OR UPDATE ON devilry_group_feedbackset
            FOR EACH ROW
                EXECUTE PROCEDURE devilry_dbcache_on_feedbackset_insert_or_update();


        /*
        Autocreate first FeedbackSet when creating an AssignmentGroup.
        */
        CREATE OR REPLACE FUNCTION devilry_dbcache_on_assignmentgroup_insert() RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO devilry_group_feedbackset (
                group_id,
                created_datetime,
                feedbackset_type,
                gradeform_data_json)
            VALUES (
                NEW.id,
                now(),
                'first_attempt',
                '');
            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS devilry_dbcache_on_assignmentgroup_insert_trigger
            ON core_assignmentgroup;
        CREATE TRIGGER devilry_dbcache_on_assignmentgroup_insert_trigger
            AFTER INSERT ON core_assignmentgroup
            FOR EACH ROW
                EXECUTE PROCEDURE devilry_dbcache_on_assignmentgroup_insert();


        /*
        Autoupdate AssignmentGroupCachedData.*_comment_count fields automatically.
        */
        /*
        CREATE OR REPLACE FUNCTION devilry_dbcache_on_group_or_imageannotationcomment_change() RETURNS TRIGGER AS $$
        DECLARE
            var_basecomment record;
        BEGIN
            SELECT user_role
            FROM devilry_comment.comment WHERE id = NEW.id
            INTO var_basecomment;

            IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                IF TG_OP = 'INSERT' THEN
                    IF NEW.visibility = 'important' THEN
                        UPDATE devilry_dbcache_assignmentgroupcacheddata
                        SET public_total_comment_count = public_total_comment_count + 1
                        WHERE id = NEW.group_id;
                    ELSEIF  NEW.vote_type = 'unimportant' THEN
                    END IF;
                END IF;
            ELSEIF TG_OP = 'DELETE' THEN

            END IF;

            RETURN NEW;
        END
        $$ LANGUAGE plpgsql;

        DROP TRIGGER IF EXISTS devilry_dbcache_on_group_change_trigger
            ON devilry_group_groupcomment;
        CREATE TRIGGER devilry_dbcache_on_group_change_trigger
            AFTER INSERT UPDATE OR OR DELETE ON devilry_group_groupcomment
            FOR EACH ROW
                EXECUTE PROCEDURE devilry_dbcache_on_group_or_imageannotationcomment_change();

        DROP TRIGGER IF EXISTS devilry_dbcache_on_group_imageannotationcomment_trigger
            ON devilry_group_imageannotationcomment;
        CREATE TRIGGER devilry_dbcache_on_group_imageannotationcomment_trigger
            AFTER INSERT OR UPDATE OR DELETE ON devilry_group_imageannotationcomment
            FOR EACH ROW
                EXECUTE PROCEDURE devilry_dbcache_on_group_or_imageannotationcomment_change();
        */
    """)


class TestFeedbackSetTriggers(test.TestCase):
    def setUp(self):
        _create_triggers()

    def test_create_feedbackset_sanity(self):
        group = mommy.make('core.AssignmentGroup')
        autocreated_feedbackset = group.feedbackset_set.first()
        feedbackset = mommy.make('devilry_group.FeedbackSet', group=group)
        cached_data = AssignmentGroupCachedData.objects.get(group=feedbackset.group)
        self.assertEqual(autocreated_feedbackset, cached_data.first_feedbackset)
        self.assertEqual(feedbackset, cached_data.last_feedbackset)
        self.assertIsNone(cached_data.last_published_feedbackset)

    def test_create_published_feedbackset(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet',
                                 grading_published_datetime=timezone.now())
        cached_data = AssignmentGroupCachedData.objects.get(group=feedbackset.group)
        self.assertEqual(feedbackset, cached_data.last_published_feedbackset)

    def test_update_feedbackset_to_published_sanity(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', grading_published_datetime=None)
        feedbackset.grading_published_datetime = timezone.now()
        feedbackset.save()
        cached_data = AssignmentGroupCachedData.objects.get(group=feedbackset.group)
        self.assertEqual(feedbackset, cached_data.last_published_feedbackset)

    def test_update_feedbackset_to_unpublished_sanity(self):
        feedbackset = mommy.make('devilry_group.FeedbackSet', grading_published_datetime=timezone.now())
        feedbackset.grading_published_datetime = None
        feedbackset.save()
        cached_data = AssignmentGroupCachedData.objects.get(group=feedbackset.group)
        self.assertIsNone(cached_data.last_published_feedbackset)


class TestAssignmentGroupTriggers(test.TestCase):
    def setUp(self):
        _create_triggers()

    def test_create_group_creates_feedbackset_sanity(self):
        group = mommy.make('core.AssignmentGroup')
        autocreated_feedbackset = group.feedbackset_set.first()
        self.assertIsNotNone(autocreated_feedbackset)
        self.assertEqual(FeedbackSet.FEEDBACKSET_TYPE_FIRST_ATTEMPT, autocreated_feedbackset.feedbackset_type)

    def test_create_group_creates_feedbackset_created_datetime_in_correct_timezone(self):
        # NOTE: We add 60 sec to before and after, because Django and postgres servers
        #       can be a bit out of sync with each other, and the important thing here
        #       is that the timestamp is somewhat correct (not in the wrong timezone).
        before = timezone.now() - timedelta(seconds=60)
        group = mommy.make('core.AssignmentGroup')
        after = timezone.now() + timedelta(seconds=60)
        autocreated_feedbackset = group.feedbackset_set.first()
        self.assertTrue(autocreated_feedbackset.created_datetime >= before)
        self.assertTrue(autocreated_feedbackset.created_datetime <= after)


class TimeExecution(object):
    def __init__(self, label):
        self.start_time = None
        self.label = label

    def __enter__(self):
        self.start_time = datetime.now()

    def __exit__(self, ttype, value, traceback):
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        print
        print '{}: {}s'.format(self.label, duration)
        print


class TestBenchMarkFeedbackSetTrigger(test.TestCase):
    def setUp(self):
        _remove_triggers()

    def __create_in_distinct_groups_feedbacksets(self, label):
        count = 10000
        assignment = mommy.make('core.Assignment')
        created_by = mommy.make(settings.AUTH_USER_MODEL)

        groups = []
        for x in range(count):
            groups.append(mommy.prepare('core.AssignmentGroup', parentnode=assignment))
        AssignmentGroup.objects.bulk_create(groups)

        feedbacksets = []
        for group in AssignmentGroup.objects.filter(parentnode=assignment):
            feedbackset = mommy.prepare(FeedbackSet, group=group, created_by=created_by, is_last_in_group=None)
            feedbacksets.append(feedbackset)

        with TimeExecution('{} ({})'.format(label, count)):
            FeedbackSet.objects.bulk_create(feedbacksets)

    def test_create_feedbacksets_in_distinct_groups_without_triggers(self):
        self.__create_in_distinct_groups_feedbacksets('feedbacksets distinct groups: no triggers')

    def test_create_feedbacksets_in_distinct_groups_with_triggers(self):
        _create_triggers()
        self.__create_in_distinct_groups_feedbacksets('feedbacksets distinct groups: with triggers')

    def __create_in_same_group_feedbacksets(self, label):
        count = 1000
        assignment = mommy.make('core.Assignment')
        created_by = mommy.make(settings.AUTH_USER_MODEL)
        group = mommy.make('core.AssignmentGroup', parentnode=assignment)

        feedbacksets = []
        for x in range(count):
            feedbackset = mommy.prepare(FeedbackSet, group=group, created_by=created_by, is_last_in_group=None)
            feedbacksets.append(feedbackset)

        with TimeExecution('{} ({})'.format(label, count)):
            FeedbackSet.objects.bulk_create(feedbacksets)

    def test_create_feedbacksets_in_same_group_without_triggers(self):
        self.__create_in_same_group_feedbacksets('feedbacksets same group: no triggers')

    def test_create_feedbacksets_in_same_group_with_triggers(self):
        _create_triggers()
        # This should have some overhead because we need to UPDATE the AssignmentGroupCachedData
        # for each INSERT
        self.__create_in_same_group_feedbacksets('feedbacksets same group: with triggers')


class TestBenchMarkAssignmentGroupTrigger(test.TestCase):
    def setUp(self):
        _remove_triggers()

    def __create_distinct_groups(self, label):
        count = 10000
        assignment = mommy.make('core.Assignment')
        groups = []
        for x in range(count):
            groups.append(mommy.prepare('core.AssignmentGroup', parentnode=assignment))

        with TimeExecution('{} ({})'.format(label, count)):
            AssignmentGroup.objects.bulk_create(groups)

    def test_create_in_distinct_groups_without_triggers(self):
        self.__create_distinct_groups('groups: no triggers')

    def test_create_in_distinct_groups_with_triggers(self):
        _create_triggers()
        self.__create_distinct_groups('groups: with triggers')
