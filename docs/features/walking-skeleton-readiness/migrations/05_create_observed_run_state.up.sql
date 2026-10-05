CREATE TABLE IF NOT EXISTS "observed_run_state" (
	"id" uuid PRIMARY KEY NOT NULL,
	"verification_run_id" uuid NOT NULL REFERENCES "verification_run"("id"),
	"key" text NOT NULL,
	"value" text NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);

CREATE INDEX IF NOT EXISTS "observed_run_state_verification_run_id_idx" ON "observed_run_state" ("verification_run_id");