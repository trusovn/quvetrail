import { buildApp } from "./app.js";
import { parseConfig } from "./config.js";
import { createDatabase } from "./database.js";

async function start(): Promise<void> {
  const config = parseConfig(process.env);
  const connection = createDatabase(config.DATABASE_URL);
  const app = await buildApp({ checkDatabase: connection.check }, { logger: true });

  app.addHook("onClose", async () => {
    await connection.pool.end();
  });

  await app.listen({ host: config.HOST, port: config.PORT });
}

start().catch((error: unknown) => {
  console.error("API startup failed", error);
  process.exitCode = 1;
});
