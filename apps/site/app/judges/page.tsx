import Image from "next/image";

const evidence = [
  ["Observed", "Managed Codex interruption", "Owned turn stopped through the supported SDK", "PASS"],
  ["Verified", "Immutable checkpoint restore", "Selected files restored byte for byte", "PASS"],
  ["Tested", "Independent local checks", "54 core checks and 6 browser checks", "PASS"],
  ["Unavailable", "Live Strands / Bedrock", "AWS account authorization rejected every invocation", "BLOCKED"],
] as const;

export default function JudgesPage() {
  return <article className="judge-page">
    <section className="judge-hero wrap" data-film="judge-hero">
      <p className="eyebrow">Agents for Humans / Professional Agents</p>
      <h1>Judge the evidence path.</h1>
      <p className="intro">Dovet preserves approved coding state across a managed worker interruption. Every claim below is tied to observed, tested, or unavailable evidence.</p>
      <div className="release-line"><span>Submission build</span><code>v0.1.1</code><span>Local-first</span><strong>AWS invocation blocked</strong></div>
    </section>

    <section className="judge-evidence wrap" data-film="evidence">
      <div className="judge-section-title"><p className="eyebrow">Release evidence</p><h2>Four facts. No invented progress.</h2></div>
      <ol>
        {evidence.map(([kind, title, detail, status]) => <li key={title}>
          <span className="evidence-index">{kind}</span>
          <div><h3>{title}</h3><p>{detail}</p></div>
          <strong className={status === "PASS" ? "evidence-pass" : "evidence-blocked"}>{status}</strong>
        </li>)}
      </ol>
    </section>

    <section className="judge-proof" data-film="proof">
      <div className="wrap proof-layout">
        <div>
          <p className="eyebrow">Observed interruption</p>
          <h2>The process stopped. The bytes stayed.</h2>
          <p>Dovet started an owned Codex turn, observed the intentional interruption, confirmed the worker stopped, and restored the captured files byte-identically.</p>
        </div>
        <dl>
          <div><dt>Interruption</dt><dd>Observed</dd></div>
          <div><dt>Checkpoint</dt><dd><code>d3d7f1fd4940…</code></dd></div>
          <div><dt>Snapshot</dt><dd><code>37825aa7bdff…</code></dd></div>
          <div><dt>Restore</dt><dd>Byte-identical</dd></div>
        </dl>
      </div>
    </section>

    <section className="judge-architecture wrap" data-film="architecture">
      <div className="judge-section-title"><p className="eyebrow">Durability boundary</p><h2>The bridge can stop. The supervisor remains.</h2><p>The stdio plugin connects Codex to an independent loopback daemon. SQLite, immutable objects, approvals, budgets, and single-writer leases remain outside the host process.</p></div>
      <Image src="/architecture.svg" alt="Dovet architecture showing the Codex bridge, independent local daemon and blocked AWS recovery boundary" width={1600} height={900} priority />
    </section>

    <section className="judge-blocker" data-film="blocker">
      <div className="wrap blocker-layout"><div><p className="eyebrow">Provider evidence</p><h2>Unknown never becomes green.</h2></div><div><strong>0 successful provider requests</strong><p>Agreement, entitlement, region, and model discovery passed. Bedrock authorization remained <code>NOT_AUTHORIZED</code>, so Dovet did not publish a simulated recovery as live evidence.</p></div></div>
    </section>

    <section className="judge-commands wrap" data-film="commands">
      <p className="eyebrow">Reproduce locally</p>
      <h2>One normal monorepo.</h2>
      <pre><code>pnpm setup{`\n`}pnpm doctor{`\n`}pnpm check{`\n`}pnpm test{`\n`}pnpm build{`\n`}pnpm test:e2e</code></pre>
      <p>The isolated installation check builds the Python wheel in a fresh environment and verifies the packaged migration, supervisor, restricted worker, and portable bundle importer.</p>
    </section>
  </article>;
}
