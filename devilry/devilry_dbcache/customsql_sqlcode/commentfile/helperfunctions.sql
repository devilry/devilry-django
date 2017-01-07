CREATE OR REPLACE FUNCTION devilry__get_group_id_from_comment_id(
    param_comment_id integer)
RETURNS integer AS $$
DECLARE
    var_group_id integer;
BEGIN
    SELECT devilry_group_feedbackset.group_id
    FROM devilry_comment_commentfile
    INNER JOIN devilry_comment_comment
        ON devilry_comment_comment.id = devilry_comment_commentfile.comment_id
    INNER JOIN devilry_group_groupcomment
        ON devilry_group_groupcomment.comment_ptr_id = devilry_comment_comment.id
    INNER JOIN devilry_group_feedbackset
        ON devilry_group_feedbackset.id = devilry_group_groupcomment.feedback_set_id
    WHERE
        devilry_comment_comment.id = param_comment_id
    INTO var_group_id;

    RETURN var_group_id;
END
$$ LANGUAGE plpgsql;
