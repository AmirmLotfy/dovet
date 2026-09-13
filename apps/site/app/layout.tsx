import type { Metadata } from "next";
import Link from "next/link";
import "./site.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://dovet.site";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: "Dovet - Recovery and verification for coding work", template: "%s - Dovet" },
  description: "Preserve coding-task state, recover interrupted managed runs, and verify the result with Dovet's Codex integration and Strands supervisor.",
};

function DovetMark({ size }: { size: number }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M2 5h9l3 3-3 3H2V5Zm20 14h-9l-3-3 3-3h9v6Z" /></svg>;
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const sourceUrl = process.env.NEXT_PUBLIC_SOURCE_URL;
  const demoReady = process.env.NEXT_PUBLIC_DEMO_READY === "true";
  return <html lang="en"><body><a className="skip" href="#content">Skip to content</a><header className="site-header"><Link className="wordmark" href="/" aria-label="Dovet home"><DovetMark size={22} />Dovet</Link><nav aria-label="Main navigation"><Link href="/how-it-works">How it works</Link><Link href="/demo">Demo</Link><Link href="/docs">Docs</Link>{sourceUrl ? <a href={sourceUrl}>Source</a> : null}<Link className="nav-action" href="/demo">{demoReady ? "Run the demo" : "Demo status"}</Link></nav></header><main id="content">{children}</main><footer><div><span className="wordmark"><DovetMark size={18} />Dovet</span><p>Keep the work. Change the agent.</p></div><nav aria-label="Footer navigation"><Link href="/docs">Docs</Link><Link href="/privacy">Privacy</Link><Link href="/terms">Terms</Link><Link href="/changelog">Changelog</Link></nav><p className="disclosure">Independent open-source project. Not affiliated with OpenAI or Amazon.</p></footer></body></html>;
}
