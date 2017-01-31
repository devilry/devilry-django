CREATE OR REPLACE FUNCTION devilry__on_candidate_after_insert_or_update() RETURNS TRIGGER AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(NEW.assignment_group_id);
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
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_group_id(OLD.assignment_group_id);
    IF var_group_id is NOT NULL THEN
        PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    END IF;

    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_candidate_after_delete
    ON core_candidate;
CREATE TRIGGER devilry__on_candidate_after_delete
    AFTER DELETE ON core_candidate
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_candidate_after_delete();
