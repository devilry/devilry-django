-- Takes an AssignmentGroup.id and returns the Assignment.first_deadline
-- for the assignment that the group belongs to.
CREATE OR REPLACE FUNCTION devilry__get_first_deadline_from_group_id(
    param_group_id integer)
RETURNS timestamp with time zone AS $$
DECLARE
    var_first_deadline timestamp with time zone;
BEGIN
    SELECT core_assignment.first_deadline
    FROM core_assignmentgroup
    INNER JOIN core_assignment ON
        core_assignment.id = core_assignmentgroup.parentnode_id
    WHERE core_assignmentgroup.id = param_group_id
    INTO var_first_deadline;

    RETURN var_first_deadline;
END
$$ LANGUAGE plpgsql;
