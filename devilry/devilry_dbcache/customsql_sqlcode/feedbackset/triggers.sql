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
    RETURN OLD;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_feedbackset_after_delete
    ON devilry_group_feedbackset;
CREATE TRIGGER devilry__on_feedbackset_after_delete
    AFTER DELETE ON devilry_group_feedbackset
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_feedbackset_after_delete();


CREATE OR REPLACE FUNCTION devilry__on_feedbackset_deadline_update() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.deadline_datetime <> OLD.deadline_datetime THEN
        INSERT INTO devilry_group_feedbacksetdeadlinehistory (
            feedback_set_id,
            changed_datetime,
            changed_by_id,
            deadline_old,
            deadline_new)
        VALUES (
            NEW.id,
            now(),
            NEW.last_updated_by_id,
            OLD.deadline_datetime,
            NEW.deadline_datetime);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_feedbackset_deadline_update_trigger
    ON devilry_group_feedbackset;
CREATE TRIGGER devilry__on_feedbackset_deadline_update_trigger
    AFTER UPDATE ON devilry_group_feedbackset
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_feedbackset_deadline_update();


CREATE OR REPLACE FUNCTION devilry__on_feedbackset_grading_update() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.grading_points <> OLD.grading_points THEN
        INSERT INTO devilry_group_feedbacksetgradingupdatehistory (
            feedback_set_id,
            updated_by_id,
            updated_datetime,
            old_grading_points,
            old_grading_published_by_id,
            old_grading_published_datetime)
        VALUES (
            NEW.id,
            NEW.last_updated_by_id,
            now(),
            OLD.grading_points,
            OLD.grading_published_by_id,
            OLD.grading_published_datetime);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_feedbackset_grading_update_trigger
    ON devilry_group_feedbackset;
CREATE TRIGGER devilry__on_feedbackset_grading_update_trigger
    AFTER UPDATE ON devilry_group_feedbackset
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_feedbackset_grading_update()
