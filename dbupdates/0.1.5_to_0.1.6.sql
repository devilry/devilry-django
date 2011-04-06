alter table grade_rstschema_rstschemadefinition add column "grade_to_points_mapping" text DEFAULT NULL;
alter table core_assignment add column "students_can_see_points" boolean NOT NULL DEFAULT true;
