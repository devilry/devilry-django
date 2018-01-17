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
