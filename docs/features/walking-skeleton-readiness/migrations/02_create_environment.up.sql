CREATE TABLE IF NOT EXISTS "environment" (
	"id" uuid PRIMARY KEY NOT NULL,
	"project_id" uuid NOT NULL REFERENCES "project"("id"),
	"name" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS "environment_project_id_idx" ON "environment" ("project_id");