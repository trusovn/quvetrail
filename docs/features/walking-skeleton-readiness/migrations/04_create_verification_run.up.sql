CREATE TABLE IF NOT EXISTS "verification_run" (
	"id" uuid PRIMARY KEY NOT NULL,
	"verification_target_id" uuid NOT NULL REFERENCES "verification_target"("id"),
	"run_reference" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS "verification_run_verification_target_id_idx" ON "verification_run" ("verification_target_id");