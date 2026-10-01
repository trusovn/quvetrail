import { existsSync } from "node:fs";
import { rm, writeFile } from "node:fs/promises";
import { spawnSync } from "node:child_process";

const sentinel = new URL("../apps/web/src/__architecture_sentinel__.ts", import.meta.url);

if (existsSync(sentinel)) {
  throw new Error(`Refusing to overwrite existing sentinel path: ${sentinel.pathname}`);
}

try {
  await writeFile(sentinel, 'import "../../api/src/database.js";\n');
  const result = spawnSync("pnpm", ["check:architecture:tree"], {
    cwd: new URL("..", import.meta.url),
    encoding: "utf8",
  });
  const output = `${result.stdout ?? ""}\n${result.stderr ?? ""}`;

  if (result.status === 0 || !output.includes("no-web-to-server")) {
    throw new Error(`Architecture sentinel was not rejected by no-web-to-server:\n${output}`);
  }

  console.log("Architecture sentinel OK: no-web-to-server rejected the forbidden import");
} finally {
  await rm(sentinel, { force: true });
}
