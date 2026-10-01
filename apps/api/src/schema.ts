import { integer, pgTable, text, timestamp } from "drizzle-orm/pg-core";

// Technical-only state used to prove migration and restart persistence before
// product entities are introduced.
export const foundationProbe = pgTable("foundation_probe", {
  id: integer().primaryKey(),
  token: text().notNull(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});
