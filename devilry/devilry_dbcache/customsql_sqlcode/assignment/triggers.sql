-- Auto-update first feedbacksets with deadline_datetime same as OLD.first_deadline
CREATE OR REPLACE FUNCTION devilry__assignment_first_deadline_update() RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' AND NEW.first_deadline != OLD.first_deadline THEN
      UPDATE devilry_group_feedbackset
      SET deadline_datetime = NEW.first_deadline
      WHERE id IN (
              SELECT devilry_group_feedbackset.id
              FROM devilry_group_feedbackset
              INNER JOIN core_assignmentgroup ON
                  core_assignmentgroup.id = devilry_group_feedbackset.group_id
              WHERE
                core_assignmentgroup.parentnode_id = NEW.id
                AND
                feedbackset_type = 'first_attempt'
                AND
                deadline_datetime = OLD.first_deadline
          );
    END IF;
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS devilry__assignment_first_deadline_update_trigger
    ON core_assignment;
CREATE TRIGGER devilry__assignment_first_deadline_update_trigger
    AFTER UPDATE ON core_assignment
    FOR EACH ROW
        EXECUTE PROCEDURE devilry__assignment_first_deadline_update();
