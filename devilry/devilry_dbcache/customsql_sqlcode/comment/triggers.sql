--
-- Create logging model for changes in GroupComments.
--
-- We need to operate on the devilry_comment_comment table as this is
-- where the field values are stored.

CREATE OR REPLACE FUNCTION devilry__on_comment_text_update() RETURNS TRIGGER AS $$
DECLARE
    var_existing_commentedithistory_id INTEGER;
BEGIN
    IF OLD.id != NEW.id THEN
        RAISE EXCEPTION 'OLD.id #% != NEW.id #%', OLD.id, NEW.id;
    END IF;

    SELECT id
    FROM devilry_comment_commentedithistory
    WHERE edited_datetime = now() AND comment_id = NEW.id
    INTO var_existing_commentedithistory_id;

    IF TG_OP = 'UPDATE' AND var_existing_commentedithistory_id IS NULL THEN
        INSERT INTO devilry_comment_commentedithistory (
            comment_id,
            edited_by_id,
            edited_datetime,
            pre_edit_text,
            post_edit_text)
        VALUES (
            NEW.id,
            NEW.user_id,
            now(),
            OLD.text,
            NEW.text);
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__on_comment_text_update_trigger
    ON devilry_comment_comment;
CREATE TRIGGER devilry__on_comment_text_update_trigger
    AFTER UPDATE ON devilry_comment_comment
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__on_comment_text_update();