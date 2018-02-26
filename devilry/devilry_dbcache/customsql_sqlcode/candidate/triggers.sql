CREATE OR REPLACE FUNCTION devilry__on_candidate_after_insert_or_update() RETURNS TRIGGER AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(NEW.assignment_group_id);
    IF TG_OP = 'UPDATE' AND NEW.assignment_group_id != OLD.assignment_group_id THEN
        PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.assignment_group_id);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_candidate_after_insert_or_update
    ON core_candidate;
CREATE TRIGGER devilry__on_candidate_after_insert_or_update
    AFTER INSERT OR UPDATE ON core_candidate
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_candidate_after_insert_or_update();


CREATE OR REPLACE FUNCTION devilry__on_candidate_after_delete() RETURNS TRIGGER AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.assignment_group_id);
    RETURN OLD;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_candidate_after_delete
    ON core_candidate;
CREATE TRIGGER devilry__on_candidate_after_delete
    AFTER DELETE ON core_candidate
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_candidate_after_delete();


--
-- Create a new core_candidateassignmentgrouphistory when a core_candidate entry is
-- inserted.
--
CREATE OR REPLACE FUNCTION devilry__on_candidate_insert_add_history() RETURNS TRIGGER AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'INSERT' THEN
        SELECT user_id
        FROM core_relatedstudent
        WHERE id = NEW.relatedstudent_id
        INTO var_user_id;
        INSERT INTO core_candidateassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            NEW.assignment_group_id,
            var_user_id,
            now(),
            TRUE);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE  plpgsql;

DROP TRIGGER IF EXISTS devilry__on_candidate_insert_add_history_trigger
    ON core_candidate;
CREATE TRIGGER devilry__on_candidate_insert_add_history_trigger
    AFTER INSERT ON core_candidate
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_candidate_insert_add_history();


--
-- Create a new core_candidateassignmentgrouphistory when core_candidate.assignment_group_id
-- is updated/changed.
--
CREATE OR REPLACE FUNCTION devilry__on_candidate_update_add_history() RETURNS TRIGGER AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.assignment_group_id <> OLD.assignment_group_id THEN
        SELECT user_id
        FROM core_relatedstudent
        WHERE id = NEW.relatedstudent_id
        INTO var_user_id;

        -- We create a history entry for the group the user was added to.
        INSERT INTO core_candidateassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            NEW.assignment_group_id,
            var_user_id,
            now(),
            TRUE);

        -- And we create a history entry for the group the user was removed from.
        INSERT INTO core_candidateassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            OLD.assignment_group_id,
            var_user_id,
            now(),
            FALSE);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE  plpgsql;

DROP TRIGGER IF EXISTS devilry__on_candidate_update_add_history_trigger
    ON core_candidate;
CREATE TRIGGER devilry__on_candidate_update_add_history_trigger
    AFTER UPDATE ON core_candidate
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_candidate_update_add_history();


--
-- Create a new core_candidateassignmentgrouphistory when a core_candidate entry is
-- deleted.
--
CREATE OR REPLACE FUNCTION devilry__on_candidate_delete_add_history() RETURNS TRIGGER AS $$
DECLARE
    var_user_id integer;
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF EXISTS (
              SELECT 1
              FROM core_assignmentgroup
              WHERE id = OLD.assignment_group_id AND internal_is_being_deleted = TRUE
            ) THEN
            RETURN NULL;
        END IF;

        SELECT user_id
        FROM core_relatedstudent
        WHERE id = OLD.relatedstudent_id
        INTO var_user_id;
        INSERT INTO core_candidateassignmentgrouphistory (
            assignment_group_id,
            user_id,
            created_datetime,
            is_add)
        VALUES (
            OLD.assignment_group_id,
            var_user_id,
            now(),
            FALSE);
        RETURN OLD;
    END IF;
END
$$ LANGUAGE  plpgsql;

DROP TRIGGER IF EXISTS devilry__on_candidate_delete_add_history_trigger
    ON core_candidate;
CREATE TRIGGER devilry__on_candidate_delete_add_history_trigger
    AFTER DELETE ON core_candidate
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_candidate_delete_add_history();
