CREATE OR REPLACE FUNCTION devilry__create_first_feedbackset_in_group(
    param_group_id integer)
RETURNS VOID AS $$
DECLARE
    var_first_deadline timestamp with time zone;
BEGIN
    var_first_deadline = devilry__get_first_deadline_from_group_id(param_group_id);

    INSERT INTO devilry_group_feedbackset (
        group_id,
        created_datetime,
        feedbackset_type,
        gradeform_data_json,
        ignored,
        ignored_reason,
        deadline_datetime)
    VALUES (
        param_group_id,
        now(),
        'first_attempt',
        '',
        FALSE,
        '',
        var_first_deadline);
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


CREATE OR REPLACE FUNCTION devilry__is_first_feedbackset_in_group(
    param_feedbackset_id integer,
    param_group_id boolean,
    param_is_update_operation boolean)
RETURNS boolean AS $$
DECLARE
    var_first_feedbackset_id integer;
    var_is_first_feedbackset boolean;
BEGIN
    SELECT id
    FROM devilry_group_feedbackset
    WHERE group_id = param_group_id
    ORDER BY deadline_datetime ASC NULLS FIRST
    LIMIT 1
    INTO var_first_feedbackset_id;

    var_is_first_feedbackset = false;
    IF var_first_feedbackset_id IS NULL THEN
        var_is_first_feedbackset = true;
    ELSE
        IF param_is_update_operation AND param_feedbackset_id = var_first_feedbackset_id THEN
            var_is_first_feedbackset = true;
        END IF;
    END IF;

    RETURN var_is_first_feedbackset;
END
$$ LANGUAGE plpgsql;
