CREATE TABLE "foundation_probe" (
	"id" integer PRIMARY KEY NOT NULL,
	"token" text NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL
);
