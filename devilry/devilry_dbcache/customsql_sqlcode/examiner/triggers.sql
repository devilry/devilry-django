CREATE OR REPLACE FUNCTION devilry__on_examiner_after_insert_or_update() RETURNS TRIGGER AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(NEW.assignmentgroup_id);
    IF TG_OP = 'UPDATE' AND NEW.assignmentgroup_id != OLD.assignmentgroup_id THEN
        PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.assignmentgroup_id);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_examiner_after_insert_or_update
    ON core_assignmentgroup_examiners;
CREATE TRIGGER devilry__on_examiner_after_insert_or_update
    AFTER INSERT OR UPDATE ON core_assignmentgroup_examiners
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_examiner_after_insert_or_update();

CREATE OR REPLACE FUNCTION devilry__on_examiner_after_delete() RETURNS TRIGGER AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.assignmentgroup_id);
    RETURN OLD;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_examiner_after_delete
    ON core_assignmentgroup_examiners;
CREATE TRIGGER devilry__on_examiner_after_delete
    AFTER DELETE ON core_assignmentgroup_examiners
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_examiner_after_delete();

--
-- Create a new core_examinerassignmentgrouphistory when a core_assignmentgroup_examiners entry is
-- inserted.
--
CREATE OR REPLACE FUNCTION devilry__on_examiner_insert_add_history() RETURNS TRIGGER AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'INSERT' THEN
        SELECT user_id
        FROM core_relatedexaminer
        WHERE id = NEW.relatedexaminer_id
        INTO var_user_id;
        INSERT INTO core_examinerassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            NEW.assignmentgroup_id,
            var_user_id,
            now(),
            TRUE);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE  plpgsql;

DROP TRIGGER IF EXISTS devilry__on_examiner_insert_add_history_trigger
    ON core_assignmentgroup_examiners;
CREATE TRIGGER devilry__on_examiner_insert_add_history_trigger
    AFTER INSERT ON core_assignmentgroup_examiners
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_examiner_insert_add_history();


--
-- Create a new core_examinerassignmentgrouphistory when core_assignmentgroup_examiners.assignmentgroup_id
-- is updated/changed.
--
CREATE OR REPLACE FUNCTION devilry__on_examiner_update_add_history() RETURNS TRIGGER AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.assignmentgroup_id <> OLD.assignmentgroup_id THEN
        SELECT user_id
        FROM core_relatedexaminer
        WHERE id = NEW.relatedexaminer_id
        INTO var_user_id;

        -- We create a history entry for the group the user was added to.
        INSERT INTO core_examinerassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            NEW.assignmentgroup_id,
            var_user_id,
            now(),
            TRUE);

        -- And we create a history entry for the group the user was removed from.
        INSERT INTO core_examinerassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            OLD.assignmentgroup_id,
            var_user_id,
            now(),
            FALSE);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE  plpgsql;

DROP TRIGGER IF EXISTS devilry__on_examiner_update_add_history_trigger
    ON core_assignmentgroup_examiners;
CREATE TRIGGER devilry__on_examiner_update_add_history_trigger
    AFTER UPDATE ON core_assignmentgroup_examiners
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_examiner_update_add_history();


--
-- Create a new core_examinerassignmentgrouphistory when a core_assignmentgroup_examiners entry is
-- deleted.
--
CREATE OR REPLACE FUNCTION devilry__on_examiner_delete_add_history() RETURNS TRIGGER AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF EXISTS (
                SELECT 1
                FROM core_assignmentgroup
                WHERE id = OLD.assignmentgroup_id AND internal_is_being_deleted = TRUE
            ) THEN
            RETURN NULL;
        END IF;

        SELECT user_id
        FROM core_relatedexaminer
        WHERE id = OLD.relatedexaminer_id
        INTO var_user_id;
        INSERT INTO core_examinerassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            OLD.assignmentgroup_id,
            var_user_id,
            now(),
            FALSE);
        RETURN OLD;
    END IF;
END
$$ LANGUAGE  plpgsql;

DROP TRIGGER IF EXISTS devilry__on_examiner_delete_add_history_trigger
    ON core_assignmentgroup_examiners;
CREATE TRIGGER devilry__on_examiner_delete_add_history_trigger
    AFTER DELETE ON core_assignmentgroup_examiners
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_examiner_delete_add_history();
