import React from "react";
import { createRoot } from "react-dom/client";
import type { components } from "@dovet/contracts";
import { DovetMark, Status } from "@dovet/ui";
import "@dovet/ui/tokens.css";
import "./styles.css";

type Capability = { name: string; status: "ready" | "blocked" | "unavailable" | "unverified"; detail: string };
type Health = { version: string; readiness: string; capabilities: Capability[] };
type LocalStatus = { service: string; work: unknown[]; needs_you: unknown[]; history: unknown[]; message: string };
type RunEvidence = components["schemas"]["RunEvidenceView"];
type Usage = {
  observed_at: string;
  state: "known" | "unknown" | "stale" | "unavailable";
  windows: Array<{
    limit_id: string;
    window: "primary" | "secondary";
    used_percent: number;
    remaining_percent: number;
    window_minutes: number | null;
  }>;
  advice: { level: string; reason: string };
  error: string | null;
};

function useDovet() {
  const [health, setHealth] = React.useState<Health | null>(null);
  const [status, setStatus] = React.useState<LocalStatus | null>(null);
  const [usage, setUsage] = React.useState<Usage | null>(null);
  const [usageLoading, setUsageLoading] = React.useState(false);
  const [usageError, setUsageError] = React.useState<string | null>(null);
  const [run, setRun] = React.useState<RunEvidence | null>(null);
  const [runLoading, setRunLoading] = React.useState(false);
  const [runError, setRunError] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  React.useEffect(() => {
    async function connect() {
      try {
        const fragment = new URLSearchParams(location.hash.slice(1));
        const nonce = fragment.get("pair");
        if (nonce) {
          const paired = await fetch("/api/v1/session/pair", {
            method: "POST",
            credentials: "include",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ nonce }),
          });
          history.replaceState(null, "", location.pathname);
          if (!paired.ok) throw new Error("The pairing link expired. Open the console from Dovet again.");
          sessionStorage.setItem("dovet_csrf", (await paired.json()).csrf_token);
        }
        const healthResponse = await fetch("/health");
        if (!healthResponse.ok) throw new Error("The local service did not answer its health check.");
        setHealth(await healthResponse.json());
        const statusResponse = await fetch("/api/v1/status", { credentials: "include" });
        if (statusResponse.ok) setStatus(await statusResponse.json());
        const match = location.pathname.match(/^\/runs\/([A-Za-z0-9_-]{1,80})$/);
        if (match) {
          setRunLoading(true);
          const runResponse = await fetch(`/api/v1/runs/${match[1]}`, { credentials: "include" });
          if (!runResponse.ok) {
            const detail = await runResponse.json().catch(() => null) as { detail?: string } | null;
            throw new Error(detail?.detail ?? "Verified run evidence is unavailable.");
          }
          setRun(await runResponse.json());
        }
      } catch (caught) {
        const message = caught instanceof Error ? caught.message : "Dovet is unavailable.";
        if (location.pathname.startsWith("/runs/")) setRunError(message);
        else setError(message);
      } finally {
        setRunLoading(false);
      }
    }
    void connect();
  }, []);
  const refreshUsage = React.useCallback(async () => {
    setUsageLoading(true);
    setUsageError(null);
    try {
      const response = await fetch("/api/v1/connections/codex/usage", { credentials: "include" });
      if (!response.ok) throw new Error("Pair the console with Dovet before reading Codex usage.");
      setUsage(await response.json());
    } catch (caught) {
      setUsageError(caught instanceof Error ? caught.message : "Codex usage is unavailable.");
    } finally {
      setUsageLoading(false);
    }
  }, []);
  return { health, status, error, usage, usageLoading, usageError, refreshUsage, run, runLoading, runError };
}

function shortHash(value: string) {
  return value.slice(0, 12);
}

function RunDetail({ run }: { run: RunEvidence }) {
  return <section className="run-detail" data-testid="verified-receipt" aria-labelledby="run-title">
    <div className="run-heading">
      <div>
        <p className="eyebrow">LIVE RECEIPT / {run.project.toUpperCase()}</p>
        <h1 id="run-title">{run.title}</h1>
        <p className="lede">Managed Codex interruption to verified Bedrock recovery.</p>
      </div>
      <Status tone="ready">Checks passed</Status>
    </div>
    <dl className="run-facts" aria-label="Run evidence">
      <div><dt>Run</dt><dd><code>{run.run_id}</code></dd></div>
      <div><dt>Worker</dt><dd>{run.model_id}</dd></div>
      <div><dt>Snapshot</dt><dd><code>{shortHash(run.final_snapshot_sha256)}</code></dd></div>
      <div><dt>Release</dt><dd><code>{run.release_commit.slice(0, 9)}</code></dd></div>
    </dl>
    <div className="run-layout">
      <section className="evidence-panel" aria-labelledby="evidence-title">
        <div className="section-head"><h2 id="evidence-title">Evidence rail</h2><span>{run.events.length} records</span></div>
        <ol className="evidence-rail">
          {run.events.map((event) => <li key={event.id}>
            <span className="rail-node" aria-hidden="true" />
            <div className="event-copy">
              <span className={`knowledge knowledge--${event.knowledge_kind}`}>{event.knowledge_kind}</span>
              <h3>{event.title}</h3>
              <p>{event.detail}</p>
            </div>
          </li>)}
        </ol>
      </section>
      <aside className="receipt" aria-labelledby="receipt-title">
        <p className="eyebrow">INDEPENDENT VERIFICATION</p>
        <h2 id="receipt-title">Receipt</h2>
        <Status tone="ready">Passed</Status>
        <dl>
          <div><dt>Suite</dt><dd><code>{shortHash(run.verification.suite_digest)}</code></dd></div>
          <div><dt>Output</dt><dd><code>{shortHash(run.verification.output_sha256)}</code></dd></div>
          <div><dt>Duration</dt><dd>{run.verification.duration_ms} ms</dd></div>
          <div><dt>Changed</dt><dd>{run.changed_paths.length} authorized path{run.changed_paths.length === 1 ? "" : "s"}</dd></div>
        </dl>
        <p className="receipt-note">The worker reported a candidate. Dovet assigned the verified status only after the protected suite passed on this snapshot.</p>
      </aside>
    </div>
  </section>;
}

function App() {
  const { health, status, error, usage, usageLoading, usageError, refreshUsage, run, runLoading, runError } = useDovet();
  const [view, setView] = React.useState("Work");
  const nav = ["Work", "Needs you", "History", "Projects", "Connections", "Settings"];
  return (
    <div className="shell">
      <aside className="sidebar">
        <a className="brand" href="#work" aria-label="Dovet home"><DovetMark /><span>Dovet</span></a>
        <nav aria-label="Primary">
          {nav.map((item, index) => <React.Fragment key={item}>
            {index === 3 && <div className="nav-rule" />}
            <button className={view === item ? "nav-item active" : "nav-item"} onClick={() => setView(item)}>{item}</button>
          </React.Fragment>)}
        </nav>
        <div className="service-state">
          <span className={health ? "dot ready" : "dot"} aria-hidden="true" />
          <span>{health ? "Local service connected" : "Connecting to local service"}</span>
        </div>
      </aside>
      <main className="main" id="main-content">
        <header className="topbar"><span>Local workspace</span><span>Dovet {health?.version ?? "connecting"}</span></header>
        <section className="content">
          {runLoading && <div className="run-loading" role="status">Validating recovery receipt…</div>}
          {runError && <div className="notice danger" role="alert"><strong>Evidence unavailable.</strong><span>{runError}</span></div>}
          {run && <RunDetail run={run} />}
          {!run && !runLoading && !runError && <>
          <div className="title-row"><div><p className="eyebrow">DOVET / LOCAL</p><h1>{view}</h1><p className="lede">{view === "Work" ? "Your active coding tasks." : "Evidence from managed work."}</p></div></div>
          {error && <div className="notice danger" role="alert"><strong>Local worker unavailable.</strong><span>{error}</span></div>}
          {view === "Work" && <section aria-labelledby="active-work">
            <div className="section-head"><h2 id="active-work">Active work</h2><span>{status?.work.length ?? 0} tasks</span></div>
            <div className="empty">
              <div className="join-mark" aria-hidden="true"><span /><i /><span /></div>
              <h3>No protected work yet</h3>
              <p>{status?.message ?? "Pair this console with the local service to inspect managed work."}</p>
              <code>dovet serve --pair</code>
            </div>
          </section>}
          {view === "Connections" && <>
            <section className="usage-panel" aria-labelledby="codex-usage-title">
              <div>
                <p className="eyebrow">SUPPORTED APP-SERVER READ</p>
                <h2 id="codex-usage-title">Codex usage</h2>
              </div>
              <button className="quiet" disabled={usageLoading} onClick={() => void refreshUsage()}>
                {usageLoading ? "Reading…" : usage ? "Refresh" : "Read usage"}
              </button>
              {usageError && <p className="usage-message danger-text" role="alert">{usageError}</p>}
              {!usage && !usageError && <p className="usage-message">Read the authenticated Codex window without copying credentials or account files.</p>}
              {usage && <div className="usage-result">
                <div className="usage-state"><Status tone={usage.state === "known" ? "ready" : "warning"}>{usage.state}</Status><span>{usage.advice.level}</span></div>
                {usage.windows.map((window) => <div className="usage-window" key={`${window.limit_id}-${window.window}`}>
                  <span>{window.limit_id} / {window.window}</span>
                  <strong>{window.remaining_percent}% remaining</strong>
                </div>)}
                <p>{usage.advice.reason}</p>
                <small>Observed {new Date(usage.observed_at).toLocaleString()}</small>
              </div>}
            </section>
            <section className="capabilities" aria-label="Connections">
              {(health?.capabilities ?? []).map((capability) => <article key={capability.name}>
                <div><h2>{capability.name.replaceAll("_", " ")}</h2><p>{capability.detail}</p></div>
                <Status tone={capability.status === "ready" ? "ready" : capability.status === "blocked" ? "danger" : "warning"}>{capability.status}</Status>
              </article>)}
            </section>
          </>}
          {view !== "Work" && view !== "Connections" && <div className="empty compact"><h3>No recorded entries</h3><p>This view fills only from persisted Dovet events.</p></div>}
          </>}
        </section>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
