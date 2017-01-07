CREATE OR REPLACE FUNCTION devilry__create_first_feedbackset_in_group(
    param_group_id integer)
RETURNS VOID AS $$
BEGIN
    INSERT INTO devilry_group_feedbackset (
        group_id,
        created_datetime,
        feedbackset_type,
        gradeform_data_json,
        ignored,
        ignored_reason)
    VALUES (
        param_group_id,
        now(),
        'first_attempt',
        '',
        FALSE,
        '');
END
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION devilry__get_group_id_from_feedbackset_id(
    param_feedbackset_id integer)
RETURNS integer AS $$
DECLARE
    var_group_id integer;
BEGIN
    SELECT group_id
    FROM devilry_group_feedbackset
    WHERE id = param_feedbackset_id
    INTO var_group_id;

    RETURN var_group_id;
END
$$ LANGUAGE plpgsql;
