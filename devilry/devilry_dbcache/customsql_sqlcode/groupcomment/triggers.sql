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
    PERFORM devilry__rebuild_assignmentgroupcacheddata(var_group_id);
    RETURN OLD;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_groupcomment_after_delete
    ON devilry_group_groupcomment;
CREATE TRIGGER devilry__on_groupcomment_after_delete
    AFTER DELETE ON devilry_group_groupcomment
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_groupcomment_after_delete();


--
-- Create logging model for changes in GroupComments.
--
-- We need to operate on the devilry_comment_comment table as this is
-- where the field values are stored.
--
CREATE OR REPLACE FUNCTION devilry__on_group_comment_text_update() RETURNS TRIGGER AS $$
DECLARE
    var_comment_edit_history_id INTEGER;
BEGIN
    IF OLD.comment_ptr_id != NEW.comment_ptr_id THEN
        RAISE EXCEPTION 'OLD.comment_ptr_id #% != NEW.comment_ptr_id #%', OLD.comment_ptr_id, NEW.comment_ptr_id;
    END IF;

    SELECT id
    FROM devilry_comment_commentedithistory
    WHERE comment_id = NEW.comment_ptr_id AND edited_datetime = now()
    INTO var_comment_edit_history_id;

    IF TG_OP = 'UPDATE' AND var_comment_edit_history_id IS NOT NULL THEN
        INSERT INTO devilry_group_groupcommentedithistory (
            commentedithistory_ptr_id,
            group_comment_id,
            visibility)
        VALUES (
            var_comment_edit_history_id,
            OLD.comment_ptr_id,
            OLD.VISIBILITY);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_group_comment_text_update_trigger
   ON devilry_group_groupcomment;
CREATE TRIGGER devilry__on_group_comment_text_update_trigger
   AFTER UPDATE ON devilry_group_groupcomment
   FOR EACH ROW
       EXECUTE PROCEDURE devilry__on_group_comment_text_update();
