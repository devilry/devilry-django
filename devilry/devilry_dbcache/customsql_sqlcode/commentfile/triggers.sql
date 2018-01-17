CREATE OR REPLACE FUNCTION devilry__on_commentfile_after_insert_or_update() RETURNS TRIGGER AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_comment_id(NEW.comment_id);
    IF var_group_id IS NOT NULL THEN
        PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_commentfile_after_insert_or_update_trigger
    ON devilry_comment_commentfile;
CREATE TRIGGER devilry__on_commentfile_after_insert_or_update_trigger
    AFTER INSERT OR UPDATE ON devilry_comment_commentfile
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_commentfile_after_insert_or_update();


CREATE OR REPLACE FUNCTION devilry__on_commentfile_after_delete() RETURNS TRIGGER AS $$
DECLARE
    var_group_id integer;
BEGIN
    var_group_id = devilry__get_group_id_from_comment_id(OLD.comment_id);
    IF var_group_id IS NOT NULL THEN
        PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    END IF;
    RETURN OLD;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_commentfile_after_delete
    ON devilry_comment_commentfile;
CREATE TRIGGER devilry__on_commentfile_after_delete
    AFTER DELETE ON devilry_comment_commentfile
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_commentfile_after_delete();
