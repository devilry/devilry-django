CREATE OR REPLACE FUNCTION devilry__get_group_id_from_group_id(
    param_group_id integer)
RETURNS integer AS $$
DECLARE
    var_group_id integer;
BEGIN
    SELECT core_assignment.id
    FROM core_assignment
    WHERE
        core_assignment.id = param_group_id
    INTO var_group_id;

    RETURN var_group_id;
END
$$ LANGUAGE plpgsql;
