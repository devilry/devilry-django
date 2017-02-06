CREATE OR REPLACE FUNCTION devilry__validate_feedbackset_change(
    param_feedbackset devilry_group_feedbackset,
    param_tg_op text)
RETURNS VOID AS $$
-- DECLARE
--     var_first_feedbackset_id integer;
--     var_draft_feedbackset_id integer;
--     var_is_first_feedbackset boolean;
BEGIN

--     SELECT id
--     FROM devilry_group_feedbackset
--     WHERE group_id = param_feedbackset.group_id
--     ORDER BY deadline_datetime ASC NULLS FIRST
--     LIMIT 1
--     INTO var_first_feedbackset_id;
--
--     var_is_first_feedbackset = false;
--     IF var_first_feedbackset_id IS NULL THEN
--         var_is_first_feedbackset = true;
--     ELSE
--         IF param_tg_op = 'UPDATE' AND param_feedbackset.id = var_first_feedbackset_id THEN
--             var_is_first_feedbackset = true;
--         END IF;
--     END IF;
--
--     IF var_is_first_feedbackset THEN
--         IF param_feedbackset.deadline_datetime IS NOT NULL THEN
--             RAISE EXCEPTION integrity_constraint_violation
--                 USING MESSAGE = 'The first FeedbackSet in an AssignmentGroup must have deadline_datetime=NULL';
--         END IF;
--     ELSE
--         IF param_feedbackset.deadline_datetime IS NULL THEN
--             RAISE EXCEPTION integrity_constraint_violation
--                 USING MESSAGE = 'Only the first FeedbackSet in an AssignmentGroup can have deadline_datetime=NULL';
--         END IF;
--     END IF;

-- --     RAISE LOG 'param_feedbackset: %', param_feedbackset;
-- --     RAISE LOG 'var_is_first_feedbackset: %', var_is_first_feedbackset;
END
$$ LANGUAGE plpgsql;
