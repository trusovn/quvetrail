import { fileURLToPath } from "node:url";
import { migrate } from "drizzle-orm/node-postgres/migrator";
import { parseConfig } from "./config.js";
import { createDatabase } from "./database.js";

async function run(): Promise<void> {
  const config = parseConfig(process.env);
  const connection = createDatabase(config.DATABASE_URL);
  const migrationsFolder = fileURLToPath(new URL("../drizzle", import.meta.url));

  try {
    await migrate(connection.database, { migrationsFolder });
    console.log("Database migrations are current");
  } finally {
    await connection.pool.end();
  }
}

run().catch((error: unknown) => {
  console.error("Database migration failed", error);
  process.exitCode = 1;
});
