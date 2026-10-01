/** @type {import('dependency-cruiser').IConfiguration} */
module.exports = {
  forbidden: [
    {
      name: "no-web-to-server",
      severity: "error",
      comment: "Browser code must use the HTTP API and may not import API or database internals.",
      from: { path: "^apps/web/" },
      to: { path: "^apps/api/" },
    },
    {
      name: "no-domain-to-outer-layers",
      severity: "error",
      comment: "Future deterministic domain code must remain independent of transport and persistence.",
      from: { path: "^apps/api/src/domain/" },
      to: { path: "^apps/api/src/(app|database|foundation-probe|migrate|schema|server)" },
    },
    {
      name: "no-production-to-tests",
      severity: "error",
      comment: "Production modules may not depend on test-only code.",
      from: { path: "^(apps|tools)/", pathNot: "(^|/)(test|tests)(/|$)" },
      to: { path: "(^|/)(test|tests)(/|$)" },
    },
  ],
  options: {
    doNotFollow: { path: "node_modules" },
    includeOnly: "^(apps|tools)/",
    tsPreCompilationDeps: true,
  },
};
