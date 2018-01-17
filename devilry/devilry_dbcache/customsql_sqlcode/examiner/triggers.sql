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
