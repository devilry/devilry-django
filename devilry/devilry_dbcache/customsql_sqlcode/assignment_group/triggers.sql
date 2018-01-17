-- Autocreate first FeedbackSet when creating an AssignmentGroup.
CREATE OR REPLACE FUNCTION devilry_dbcache_on_assignmentgroup_insert() RETURNS TRIGGER AS $$
BEGIN
    PERFORM devilry__create_first_feedbackset_in_group(NEW.id, NEW.parentnode_id);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry_dbcache_on_assignmentgroup_insert_trigger
    ON core_assignmentgroup;
CREATE TRIGGER devilry_dbcache_on_assignmentgroup_insert_trigger
    AFTER INSERT ON core_assignmentgroup
    FOR EACH ROW
        EXECUTE PROCEDURE devilry_dbcache_on_assignmentgroup_insert();


-- CREATE OR REPLACE FUNCTION devilry_dbcache_assignmentgroup_before_delete() RETURNS TRIGGER AS $$
-- BEGIN
--     RAISE LOG 'DELETE group';
--     RETURN OLD;
-- END
-- $$ LANGUAGE plpgsql;
--
-- DROP TRIGGER IF EXISTS devilry_dbcache_on_assignmentgroup_before_delete_trigger
--     ON core_assignmentgroup;
-- CREATE TRIGGER devilry_dbcache_on_assignmentgroup_before_delete_trigger
--     BEFORE DELETE ON core_assignmentgroup
--     FOR EACH ROW
--         EXECUTE PROCEDURE devilry_dbcache_assignmentgroup_before_delete();
