CREATE OR REPLACE FUNCTION devilry__on_feedbackset_before_insert_or_update() RETURNS TRIGGER AS $$
BEGIN
    IF pg_trigger_depth() = 1 THEN
        -- We do not validate when this is triggered via another trigger.
        -- We assume the other trigger creates/updates the feedbackset
        -- correctly.
        PERFORM devilry__validate_feedbackset_change(NEW, TG_OP);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_feedbackset_before_insert_or_update_trigger
    ON devilry_group_feedbackset;
CREATE TRIGGER devilry__on_feedbackset_before_insert_or_update_trigger
    BEFORE INSERT OR UPDATE ON devilry_group_feedbackset
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_feedbackset_before_insert_or_update();


CREATE OR REPLACE FUNCTION devilry__on_feedbackset_after_insert_or_update() RETURNS TRIGGER AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(NEW.group_id);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_feedbackset_after_insert_or_update_trigger
    ON devilry_group_feedbackset;
CREATE TRIGGER devilry__on_feedbackset_after_insert_or_update_trigger
    AFTER INSERT OR UPDATE ON devilry_group_feedbackset
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_feedbackset_after_insert_or_update();


CREATE OR REPLACE FUNCTION devilry__on_feedbackset_after_delete() RETURNS TRIGGER AS $$
BEGIN
    PERFORM devilry__rebuild_assignmentgroupcacheddata(OLD.group_id);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_feedbackset_after_delete
    ON devilry_group_feedbackset;
CREATE TRIGGER devilry__on_feedbackset_after_delete
    AFTER DELETE ON devilry_group_feedbackset
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_feedbackset_after_delete();
