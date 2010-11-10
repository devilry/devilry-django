alter table grade_rstschema_rstschemadefinition add column "maxpoints" integer unsigned NOT NULL DEFAULT 0;
alter table grade_rstschema_rstschemagrade add column "points" integer unsigned DEFAULT 0;

alter table core_period add column "minimum_points" integer unsigned NOT NULL DEFAULT 0;

alter table core_assignment add column "must_pass" bool NOT NULL DEFAULT 0;
alter table core_assignment add column "pointscale" integer unsigned NOT NULL DEFAULT 1;
alter table core_assignment add column "maxpoints" integer unsigned NOT NULL DEFAULT 0;
alter table core_assignment add column "autoscale" bool NOT NULL DEFAULT 1;
alter table core_assignment add column "attempts" integer unsigned DEFAULT NULL;

alter table core_assignmentgroup add column "points" integer unsigned NOT NULL DEFAULT 0;
alter table core_assignmentgroup add column "scaled_points" real NOT NULL DEFAULT 0.0;
alter table core_assignmentgroup add column "is_passing_grade" bool NOT NULL DEFAULT 0;
