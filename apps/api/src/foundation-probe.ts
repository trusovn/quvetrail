import { eq } from "drizzle-orm";
import { parseConfig } from "./config.js";
import { createDatabase } from "./database.js";
import { foundationProbe } from "./schema.js";

async function run(): Promise<void> {
  const [command, expectedToken] = process.argv.slice(2);
  const config = parseConfig(process.env);
  const connection = createDatabase(config.DATABASE_URL);

  try {
    if (command === "write" && expectedToken) {
      await connection.database
        .insert(foundationProbe)
        .values({ id: 1, token: expectedToken })
        .onConflictDoUpdate({
          target: foundationProbe.id,
          set: { token: expectedToken, updatedAt: new Date() },
        });
      console.log(`Foundation probe stored: ${expectedToken}`);
      return;
    }

    if (command === "read" && expectedToken) {
      const [record] = await connection.database
        .select({ token: foundationProbe.token })
        .from(foundationProbe)
        .where(eq(foundationProbe.id, 1));

      if (record?.token !== expectedToken) {
        throw new Error(`Expected foundation probe ${expectedToken}, received ${record?.token ?? "none"}`);
      }
      console.log(`Foundation probe survived restart: ${record.token}`);
      return;
    }

    throw new Error("Usage: foundation-probe <write|read> <expected-token>");
  } finally {
    await connection.pool.end();
  }
}

run().catch((error: unknown) => {
  console.error("Foundation persistence probe failed", error);
  process.exitCode = 1;
});
