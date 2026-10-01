import { sql } from "drizzle-orm";
import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";

export function createDatabase(databaseUrl: string) {
  const pool = new Pool({ connectionString: databaseUrl });
  const database = drizzle(pool);

  return {
    database,
    pool,
    async check(): Promise<void> {
      await database.execute(sql`select 1`);
    },
  };
}

export type DatabaseConnection = ReturnType<typeof createDatabase>;
