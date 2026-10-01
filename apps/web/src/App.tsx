import { useEffect, useState } from "react";

type HealthState = "checking" | "connected" | "unavailable";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:3000";

export function App() {
  const [health, setHealth] = useState<HealthState>("checking");

  useEffect(() => {
    fetch(`${apiUrl}/health`)
      .then(async (response) => {
        if (!response.ok) throw new Error(`Health request failed: ${response.status}`);
        const body = (await response.json()) as { database?: string };
        setHealth(body.database === "connected" ? "connected" : "unavailable");
      })
      .catch(() => setHealth("unavailable"));
  }, []);

  return (
    <main>
      <p className="eyebrow">QuVeTrail foundation</p>
      <h1>Full-stack shell</h1>
      <p>This page intentionally exposes infrastructure readiness only. Product behavior is deferred.</p>
      <section aria-live="polite" className={`status status--${health}`}>
        <span aria-hidden="true" />
        {health === "checking" && "Checking API and database…"}
        {health === "connected" && "API and database connected"}
        {health === "unavailable" && "API or database unavailable"}
      </section>
    </main>
  );
}
