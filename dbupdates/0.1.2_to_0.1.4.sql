ALTER TABLE core_deadline ADD COLUMN "is_head" bool NOT NULL DEFAULT(0);
ALTER TABLE core_delivery ADD COLUMN "deadline_tag_id" integer REFERENCES "core_deadline" ("id");
CREATE INDEX "core_delivery_3105f29b" ON "core_delivery" ("deadline_tag_id");


