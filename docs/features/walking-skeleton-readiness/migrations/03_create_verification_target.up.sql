CREATE TABLE IF NOT EXISTS "verification_target" (
	"id" uuid PRIMARY KEY NOT NULL,
	"environment_id" uuid NOT NULL REFERENCES "environment"("id"),
	"key" text NOT NULL,
	"value" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS "verification_target_environment_id_idx" ON "verification_target" ("environment_id");