CREATE OR REPLACE FUNCTION devilry__on_groupcomment_after_insert_or_update() RETURNS TRIGGER AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_feedbackset_id(NEW.feedback_set_id);
    PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_groupcomment_after_insert_or_update_trigger
    ON devilry_group_groupcomment;
CREATE TRIGGER devilry__on_groupcomment_after_insert_or_update_trigger
    AFTER INSERT OR UPDATE ON devilry_group_groupcomment
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_groupcomment_after_insert_or_update();


CREATE OR REPLACE FUNCTION devilry__on_groupcomment_after_delete() RETURNS TRIGGER AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_feedbackset_id(OLD.feedback_set_id);
    PERFORM devilry__rebuild_assignmentgroupcacheddata_on_delete(var_group_id, TG_TABLE_NAME);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_groupcomment_after_delete
    ON devilry_group_groupcomment;
CREATE TRIGGER devilry__on_groupcomment_after_delete
    AFTER DELETE ON devilry_group_groupcomment
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_groupcomment_after_delete();
