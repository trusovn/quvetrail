import { z } from "zod";

const configSchema = z.object({
  DATABASE_URL: z.string().url().startsWith("postgres://"),
  HOST: z.string().min(1).default("127.0.0.1"),
  PORT: z.coerce.number().int().min(1).max(65_535).default(3000),
});

export type ApiConfig = z.infer<typeof configSchema>;

export function parseConfig(environment: NodeJS.ProcessEnv): ApiConfig {
  const result = configSchema.safeParse(environment);

  if (!result.success) {
    throw new Error(`Invalid API configuration: ${z.prettifyError(result.error)}`);
  }

  return result.data;
}
