BEGIN;
CREATE TABLE "core_node_admins" (
    "id" integer NOT NULL PRIMARY KEY,
    "node_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    UNIQUE ("node_id", "user_id")
)
;
CREATE TABLE "core_node" (
    "id" integer NOT NULL PRIMARY KEY,
    "short_name" varchar(20) NOT NULL,
    "long_name" varchar(100) NOT NULL,
    "parentnode_id" integer,
    "etag" datetime NOT NULL,
    UNIQUE ("short_name", "parentnode_id")
)
;
CREATE TABLE "core_subject_admins" (
    "id" integer NOT NULL PRIMARY KEY,
    "subject_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    UNIQUE ("subject_id", "user_id")
)
;
CREATE TABLE "core_subject" (
    "id" integer NOT NULL PRIMARY KEY,
    "short_name" varchar(20) NOT NULL UNIQUE,
    "long_name" varchar(100) NOT NULL,
    "parentnode_id" integer NOT NULL REFERENCES "core_node" ("id"),
    "etag" datetime NOT NULL
)
;
CREATE TABLE "core_period_admins" (
    "id" integer NOT NULL PRIMARY KEY,
    "period_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    UNIQUE ("period_id", "user_id")
)
;
CREATE TABLE "core_period" (
    "id" integer NOT NULL PRIMARY KEY,
    "short_name" varchar(20) NOT NULL,
    "long_name" varchar(100) NOT NULL,
    "parentnode_id" integer NOT NULL REFERENCES "core_subject" ("id"),
    "start_time" datetime NOT NULL,
    "end_time" datetime NOT NULL,
    "etag" datetime NOT NULL,
    UNIQUE ("short_name", "parentnode_id")
)
;
CREATE TABLE "core_periodapplicationkeyvalue" (
    "id" integer NOT NULL PRIMARY KEY,
    "application" varchar(300) NOT NULL,
    "key" varchar(300) NOT NULL,
    "value" text,
    "period_id" integer NOT NULL REFERENCES "core_period" ("id"),
    UNIQUE ("period_id", "application", "key")
)
;
CREATE TABLE "core_relatedexaminer" (
    "id" integer NOT NULL PRIMARY KEY,
    "period_id" integer NOT NULL REFERENCES "core_period" ("id"),
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "tags" text,
    UNIQUE ("period_id", "user_id")
)
;
CREATE TABLE "core_relatedstudent" (
    "id" integer NOT NULL PRIMARY KEY,
    "period_id" integer NOT NULL REFERENCES "core_period" ("id"),
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "tags" text,
    "candidate_id" varchar(30),
    UNIQUE ("period_id", "user_id")
)
;
CREATE TABLE "core_relatedstudentkeyvalue" (
    "id" integer NOT NULL PRIMARY KEY,
    "application" varchar(300) NOT NULL,
    "key" varchar(300) NOT NULL,
    "value" text,
    "relatedstudent_id" integer NOT NULL REFERENCES "core_relatedstudent" ("id"),
    "student_can_read" bool NOT NULL,
    UNIQUE ("relatedstudent_id", "application", "key")
)
;
CREATE TABLE "core_devilryuserprofile" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id"),
    "full_name" varchar(300),
    "languagecode" varchar(100)
)
;
CREATE TABLE "core_candidate" (
    "id" integer NOT NULL PRIMARY KEY,
    "student_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "assignment_group_id" integer NOT NULL,
    "candidate_id" varchar(30),
    "identifier" varchar(30) NOT NULL,
    "full_name" varchar(300),
    "email" varchar(300),
    "etag" datetime NOT NULL
)
;
CREATE TABLE "core_assignment_admins" (
    "id" integer NOT NULL PRIMARY KEY,
    "assignment_id" integer NOT NULL,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    UNIQUE ("assignment_id", "user_id")
)
;
CREATE TABLE "core_assignment" (
    "id" integer NOT NULL PRIMARY KEY,
    "short_name" varchar(20) NOT NULL,
    "long_name" varchar(100) NOT NULL,
    "parentnode_id" integer NOT NULL REFERENCES "core_period" ("id"),
    "etag" datetime NOT NULL,
    "publishing_time" datetime NOT NULL,
    "anonymous" bool NOT NULL,
    "students_can_see_points" bool NOT NULL,
    "examiners_publish_feedbacks_directly" bool NOT NULL,
    "delivery_types" integer unsigned NOT NULL,
    "deadline_handling" integer unsigned NOT NULL,
    "scale_points_percent" integer unsigned NOT NULL,
    "first_deadline" datetime,
    UNIQUE ("short_name", "parentnode_id")
)
;
CREATE TABLE "core_assignmentgroup_examiners" (
    "id" integer NOT NULL PRIMARY KEY,
    "user_id" integer NOT NULL REFERENCES "auth_user" ("id"),
    "assignmentgroup_id" integer NOT NULL,
    UNIQUE ("user_id", "assignmentgroup_id")
)
;
CREATE TABLE "core_assignmentgroup" (
    "id" integer NOT NULL PRIMARY KEY,
    "parentnode_id" integer NOT NULL REFERENCES "core_assignment" ("id"),
    "name" varchar(30),
    "is_open" bool NOT NULL,
    "feedback_id" integer UNIQUE,
    "etag" datetime NOT NULL
)
;
CREATE TABLE "core_assignmentgrouptag" (
    "id" integer NOT NULL PRIMARY KEY,
    "assignment_group_id" integer NOT NULL REFERENCES "core_assignmentgroup" ("id"),
    "tag" varchar(20) NOT NULL,
    UNIQUE ("assignment_group_id", "tag")
)
;
CREATE TABLE "core_deadline" (
    "id" integer NOT NULL PRIMARY KEY,
    "assignment_group_id" integer NOT NULL REFERENCES "core_assignmentgroup" ("id"),
    "deadline" datetime NOT NULL,
    "text" text,
    "deliveries_available_before_deadline" bool NOT NULL,
    "feedbacks_published" bool NOT NULL
)
;
CREATE TABLE "core_filemeta" (
    "id" integer NOT NULL PRIMARY KEY,
    "delivery_id" integer NOT NULL,
    "filename" varchar(255) NOT NULL,
    "size" integer NOT NULL,
    UNIQUE ("delivery_id", "filename")
)
;
CREATE TABLE "core_delivery" (
    "id" integer NOT NULL PRIMARY KEY,
    "delivery_type" integer unsigned NOT NULL,
    "time_of_delivery" datetime NOT NULL,
    "deadline_id" integer NOT NULL REFERENCES "core_deadline" ("id"),
    "number" integer unsigned NOT NULL,
    "successful" bool NOT NULL,
    "delivered_by_id" integer REFERENCES "core_candidate" ("id"),
    "alias_delivery_id" integer UNIQUE
)
;
CREATE TABLE "core_staticfeedback" (
    "id" integer NOT NULL PRIMARY KEY,
    "delivery_id" integer NOT NULL REFERENCES "core_delivery" ("id"),
    "rendered_view" text NOT NULL,
    "grade" varchar(12) NOT NULL,
    "points" integer unsigned NOT NULL,
    "is_passing_grade" bool NOT NULL,
    "save_timestamp" datetime NOT NULL,
    "saved_by_id" integer NOT NULL REFERENCES "auth_user" ("id")
)
;
CREATE INDEX "core_node_3b069ecb" ON "core_node" ("short_name");
CREATE INDEX "core_node_6b3fcb76" ON "core_node" ("long_name");
CREATE INDEX "core_node_3e9cbb22" ON "core_node" ("parentnode_id");
CREATE INDEX "core_subject_6b3fcb76" ON "core_subject" ("long_name");
CREATE INDEX "core_subject_3e9cbb22" ON "core_subject" ("parentnode_id");
CREATE INDEX "core_period_3b069ecb" ON "core_period" ("short_name");
CREATE INDEX "core_period_6b3fcb76" ON "core_period" ("long_name");
CREATE INDEX "core_period_3e9cbb22" ON "core_period" ("parentnode_id");
CREATE INDEX "core_periodapplicationkeyvalue_edd0196a" ON "core_periodapplicationkeyvalue" ("application");
CREATE INDEX "core_periodapplicationkeyvalue_45544485" ON "core_periodapplicationkeyvalue" ("key");
CREATE INDEX "core_periodapplicationkeyvalue_40858fbd" ON "core_periodapplicationkeyvalue" ("value");
CREATE INDEX "core_periodapplicationkeyvalue_8c5e9881" ON "core_periodapplicationkeyvalue" ("period_id");
CREATE INDEX "core_relatedexaminer_8c5e9881" ON "core_relatedexaminer" ("period_id");
CREATE INDEX "core_relatedexaminer_fbfc09f1" ON "core_relatedexaminer" ("user_id");
CREATE INDEX "core_relatedstudent_8c5e9881" ON "core_relatedstudent" ("period_id");
CREATE INDEX "core_relatedstudent_fbfc09f1" ON "core_relatedstudent" ("user_id");
CREATE INDEX "core_relatedstudentkeyvalue_edd0196a" ON "core_relatedstudentkeyvalue" ("application");
CREATE INDEX "core_relatedstudentkeyvalue_45544485" ON "core_relatedstudentkeyvalue" ("key");
CREATE INDEX "core_relatedstudentkeyvalue_40858fbd" ON "core_relatedstudentkeyvalue" ("value");
CREATE INDEX "core_relatedstudentkeyvalue_a49ff7f8" ON "core_relatedstudentkeyvalue" ("relatedstudent_id");
CREATE INDEX "core_candidate_42ff452e" ON "core_candidate" ("student_id");
CREATE INDEX "core_candidate_b6550819" ON "core_candidate" ("assignment_group_id");
CREATE INDEX "core_assignment_3b069ecb" ON "core_assignment" ("short_name");
CREATE INDEX "core_assignment_6b3fcb76" ON "core_assignment" ("long_name");
CREATE INDEX "core_assignment_3e9cbb22" ON "core_assignment" ("parentnode_id");
CREATE INDEX "core_assignmentgroup_examiners_fbfc09f1" ON "core_assignmentgroup_examiners" ("user_id");
CREATE INDEX "core_assignmentgroup_examiners_bfb4165f" ON "core_assignmentgroup_examiners" ("assignmentgroup_id");
CREATE INDEX "core_assignmentgroup_3e9cbb22" ON "core_assignmentgroup" ("parentnode_id");
CREATE INDEX "core_assignmentgrouptag_b6550819" ON "core_assignmentgrouptag" ("assignment_group_id");
CREATE INDEX "core_assignmentgrouptag_58381d7c" ON "core_assignmentgrouptag" ("tag");
CREATE INDEX "core_deadline_b6550819" ON "core_deadline" ("assignment_group_id");
CREATE INDEX "core_filemeta_86628f0c" ON "core_filemeta" ("delivery_id");
CREATE INDEX "core_delivery_1b7c68" ON "core_delivery" ("deadline_id");
CREATE INDEX "core_delivery_3a443fbc" ON "core_delivery" ("delivered_by_id");
CREATE INDEX "core_staticfeedback_86628f0c" ON "core_staticfeedback" ("delivery_id");
CREATE INDEX "core_staticfeedback_59baf0a3" ON "core_staticfeedback" ("saved_by_id");
COMMIT;
