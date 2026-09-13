# 08 - Marketing website, docs and launch copy

## 1. Site scope

Build a public, English-first website on the intended domain `dovet.site`. The domain is not yet confirmed owned/available. Preview deployment must work independently of purchasing it. Centralize site URL in configuration; do not hard-code it across source files.

Routes: `/`, `/demo`, `/how-it-works`, `/docs`, `/docs/install`, `/docs/security`, `/docs/integrations`, `/docs/checkpoints`, `/changelog`, `/privacy`, `/terms`. Add a `/judges` landing page containing architecture, exact setup, tested release and demo instructions. Hide routes without actual content; do not publish empty templates.

No mandatory signup, no waitlist pretending to be the app, no fake testimonials and no pricing table for nonexistent subscriptions. Public demo and installation documentation are the conversion paths.

## 2. Navigation

Left: original Dovet wordmark. Right: How it works, Demo, Docs, Source. Primary button: **Run the demo**. Keep navigation to one row desktop and a compact accessible menu mobile. Source links to the real public repository only after it exists.

## 3. Homepage structure and exact copy

### Hero

Eyebrow: **Coding work, kept in motion.**

Headline:
**Keep the work.**
**Change the agent.**

Body:
**Dovet saves the useful state of a coding task, hands interrupted work to an authorized worker, and checks the result before calling it finished.**

Primary CTA: **Run the demo**
Secondary CTA: **Install locally**

Small qualifier: **Codex integration. Strands recovery. Your rules.**

Below the hero, show a real recorded evidence rail from the released synthetic demo. No invented customer dashboard screenshot. Provide a static accessible fallback and a clearly labeled Play recorded run action; do not autoplay with sound.

### The problem

Heading: **The interruption is only the first problem.**

Copy: **After a coding agent stops, you still have to work out what changed, what passed, what failed, and what the next worker needs to know. Dovet keeps that recovery work attached to the task.**

Use four short aligned rows, not a giant feature-card grid: Task brief / Scoped changes / Verified checks / Next action. Each links to actual evidence in the demo.

### How it works

1. **Save the working state.** A checkpoint records the approved task, selected files, evidence and last verified result.
2. **Recover within your rules.** A Strands supervisor recommends the next move. Policy, budget and workspace ownership determine whether it can proceed.
3. **Check before calling it done.** Independent verification runs against the recovered snapshot. Failed or unavailable checks stay visible.

Add the limitation immediately below: **Automatic recovery applies to Dovet-managed runs. Existing desktop sessions can be observed and handed off with your involvement.**

### Product proof

Heading: **A recovery you can inspect.**

Show one actual task receipt with a run ID, checkpoint digest, named workers and test evidence. Present measured results from that run only. When no benchmark exists, do not show a metric strip. The evidence itself is the feature.

### Boundaries

Heading: **Autonomy with an edge you can see.**

Copy: **Dovet does not rotate ChatGPT accounts, merge code for you, or let a worker approve its own permissions. It pauses when the next action needs a decision.**

Three concise permission rows: Approved paths / Authorized workers / Explicit budget. A screenshot of the real approval panel provides proof.

### Local-first, stated accurately

Heading: **Your workspace stays yours.**

Copy: **Project state and checkpoint history are stored locally by default. Your approved coding providers receive the context needed to do the task. Cloud evidence sharing is explicit, and the public demo uses synthetic code.**

Link: **Read the data boundaries**.

### Integration status

Use a small factual compatibility table generated from the release report. Initial rows: Managed Codex, Bedrock/Strands worker, Codex Desktop observation. Report tested version and limitations. No unsupported brand parade. Additional adapters can appear under an honest Roadmap section, not "Works with".

### Final CTA

Heading: **Let the next worker start with evidence.**
Buttons: **Run the demo** / **Read installation guide**.

Footer: Docs, Source, Privacy, Terms, Changelog, real contact if configured. Disclosure: **Independent open-source project. Not affiliated with OpenAI or Amazon.** Use trademarks descriptively, not as endorsement.

## 4. FAQ copy

**Does Dovet switch ChatGPT accounts?**
No. It supervises one authorized Codex identity and separately configured workers. It does not change browser cookies or rotate subscriptions.

**Can it take over every existing Codex Desktop session?**
No. Automatic recovery is for managed runs with supported control and event access. Observation mode can save approved context and help prepare a handoff.

**Does a checkpoint preserve the exact conversation?**
It preserves selected working state and evidence, not every token, hidden reasoning or unsaved data. Incomplete snapshots are identified before recovery.

**Does local-first mean code never leaves my computer?**
No. Authorized cloud coding models receive the task context permitted by your project settings. Local-first describes where Dovet stores operational state by default.

**What happens when my laptop sleeps?**
Local execution pauses. Dovet reconciles state after it returns. Cloud execution of real repositories is not silently enabled.

**Can it continue spending after my limit?**
Dovet requires a configured budget and authorized worker. It stops new dispatch when its guard denies the request. In-flight provider accounting can lag, so spending ceilings include a safety margin and are not advertised as mathematically exact billing caps.

**Does passing the checks prove the code is correct?**
It proves the recorded checks passed on the stated snapshot. It does not replace review or checks that were not configured or could not run.

## 5. Docs requirements

Installation has prerequisites, OS compatibility, exact tested version, commands, expected outputs, permission review, sample task, uninstall and troubleshooting. Clearly state whether the installer is unsigned or notarized. Never tell users to disable operating-system security indiscriminately.

Security docs explain data destinations, credentials, source isolation and known limits. Checkpoint docs document schema, import validation and export redaction. Integrations docs separate managed control from observation. Changelog entries correspond to real releases and commits.

`/judges` includes the exact demo flow, a no-paywall testing path, architecture and source links, current release SHA and how to distinguish live from replay. Do not place administrative credentials on a publicly indexed page.

## 6. SEO and performance

Server-render meaningful public copy. Page title proposal: **Dovet - Recovery and verification for coding work**. Description: **Preserve coding-task state, recover interrupted managed runs, and verify the result with Dovet's Codex integration and Strands supervisor.**

Use canonical URLs from the configured verified domain, Open Graph imagery made from actual product UI, sitemap, robots, descriptive heading hierarchy and accessible alt text. Include SoftwareApplication structured data only for truthful implemented properties; omit invented reviews/ratings/offers. Public replay and docs remain readable without client-only blank states.

Performance targets: Lighthouse accessibility >=95 in the fixed test environment, no serious/critical axe violations, CLS below 0.1, and initial marketing route JavaScript under a measured budget agreed during build. Targets are internal checks, not marketing claims. Lazy-load demo video with a poster; never ship the whole console to the homepage.

## 7. Legal/content boundaries

Privacy and terms are implementation-aligned drafts requiring owner review, not legal advice. State real collection, retention, processing locations/provider categories and contact details. Do not invent corporate registration, a compliance certificate, SOC 2 status, support guarantees or security-audit completion.

No analytics or marketing cookies by default. If later added, update disclosures/consent as needed. Screenshots, icons and demo footage must be owned or properly licensed. Do not redistribute design-reference images.
