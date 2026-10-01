import cors from "@fastify/cors";
import Fastify, { type FastifyInstance } from "fastify";

export interface AppDependencies {
  checkDatabase: () => Promise<void>;
}

export async function buildApp(
  dependencies: AppDependencies,
  options: { logger?: boolean } = {},
): Promise<FastifyInstance> {
  const app = Fastify({ logger: options.logger ?? false });

  await app.register(cors, { origin: true });

  app.get("/health", async (_request, reply) => {
    try {
      await dependencies.checkDatabase();
      return { status: "ok", database: "connected" };
    } catch (error) {
      app.log.error({ error }, "database health check failed");
      return reply.code(503).send({ status: "unavailable", database: "unavailable" });
    }
  });

  return app;
}
