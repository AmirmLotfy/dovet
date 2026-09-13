# 07 - Product UI/UX and visual specification

## 1. Design thesis

Dovet should feel like a well-made instrument for inspecting work: quiet, legible and specific. Its visual signature is a continuous evidence rail linking interruption, snapshot, replacement and verification. It is not a glowing AI brain, a generic analytics dashboard or a chat window wearing a product name.

The UI answers three questions quickly: What is working? What needs my decision? What was actually verified?

## 2. Brand

Name: **Dovet**, spoken "DOH-vet". Use the name consistently; do not fabricate a linguistic origin. Tagline: **Keep the work. Change the agent.** Intended domain: `dovet.site`, pending registrar/ownership checks. Avoid an AI suffix and exaggerated claims about autonomy.

Wordmark: plain lowercase or title-case system sans with deliberate spacing; no fake proprietary font. Mark brief: two offset solid rectangular forms that meet at a small dovetail-like notch. It should read as joining two pieces, work at 16 px and remain recognizable in one color. Build an original simple vector during implementation. Do not use a robot, sparkle, lightning bolt, infinity loop or recycled chain-link glyph.

## 3. Palette and typography

Use the supplied CSS tokens. Warm mineral background #F3F1EA, off-white surfaces #FFFEFA, near-black #242721, muted olive-gray #64685D, and dark oxide #7B362A for deliberate primary actions. Color is semantic, not decoration. Completed verification uses subdued green, needs-review uses ochre, and a failure uses dark red. Status must always include text and an icon, not just color.

UI typography uses the system sans stack, 15 px body, 13 px metadata, 12 px minimum labels and 22-28 px screen titles. Monospace is limited to paths, hashes, commands and numeric timing. Marketing headline is 56-72 px desktop and 36-44 px mobile with tight but readable line height. Do not use enormous 110 px display text that pushes the product below the fold.

No font binaries are included in this handoff. No network fonts are required to ship. Any later font adoption must include license review and avoid layout shifts.

## 4. Layout system

Desktop console: 208 px left navigation, fluid main content with max readable width around 1120 px, optional 336 px right evidence inspector. Top bar 56 px. Main padding 32 px on large screens, 20 px on medium. Tables use approximately 48-56 px rows with generous click targets. One primary action per view.

Use separators and alignment more than cards. Corners 4/8/12 px; no universal pill-shaped controls. Shadows only for floating overlays. Panels remain flat. Main work list is a row-based operational list, not six KPI tiles.

At 1024 px collapse the inspector into an accessible drawer. At 768 px collapse navigation. At 390 px show one column with project/task/status first, secondary metadata expanded on demand and a sticky safe action area. Never hide the Stop/Pause control behind a hover state. Horizontal code scrolling is contained to code blocks.

## 5. Information architecture

```text
Work
Needs you                  # badge only for actual pending decisions
History
------------------
Projects
Connections
Settings
```

No Billing, Organizations, Teams or Marketplace tabs until those features exist. Command palette: open task, filter history, checkpoint, pause, open connections. Confirmation remains required for material actions invoked by keyboard.

## 6. Screens

### S01 - First run / setup doctor

A compact checklist shows local service, Git, Codex capability, AWS credentials, model readiness and browser connection. Each row has Ready / Needs setup / Not supported plus a precise action. Never show "Connect everything" as a generic instruction. The first screen remains usable without cloud credentials; distinguish local setup success from live AI availability.

CTA: **Add a project** once core local prerequisites pass. Secondary: **Run a sample locally** for deterministic tests, clearly not a live AI recovery.

### S02 - Add project and permission review

Select path through the local application/CLI flow, then show resolved root, branch, dirty-file count, excluded categories and mode. Dirty files are listed, not silently swept into a worker. Explain managed work uses a separate worktree. Review test command templates and their trust implication.

Data-sharing review lists Code to Codex, Selected evidence to Bedrock, Cloud artifact export and Telemetry as distinct permissions. No single vague "AI access" checkbox. Confirm project budget separately.

### S03 - Work overview

Header: **Work**. Subtext: "Your active coding tasks." A narrow connection indicator says Local service connected with last heartbeat. Rows show task title/project, true status, worker, last verified criterion count, checkpoint age and a compact action menu. Empty state: "No protected work yet. Start a managed task or connect an existing project in observation mode."

Never show a task as 78% complete. Show **4 of 7 checks passing** or **Not verified yet**. Counts derive from actual evidence. A queued task is not running. A disconnected worker is not automatically failed.

### S04 - Task detail / signature evidence rail

```text
CSV import                                        Pause
Fixture project / managed worktree

Working with Bedrock     Last checkpoint 32s ago

Task        Activity        Changes        Checks
-----------------------------------------------------
10:42:11  Codex worker interrupted
          Process exit confirmed. User edits untouched.
     |
10:42:12  Checkpoint saved                    ck_... [View]
          3 scoped files captured; hashes verified.
     |
10:42:14  Recovery authorized                [Why?]
          Existing project policy; budget reserved.
     |
10:42:17  Bedrock worker started
          Continues from checkpoint ck_...
     |
          Independent checks pending
```

Values above are design examples, not seeded production claims. Production UI must render actual events. Clicking an event opens source, knowledge category, time, affected paths and linked evidence. Keep the evidence rail readable without opening every detail.

### S05 - Needs you / approval

Use a full decision panel, not a tiny ambiguous toast. Heading tells the real decision, e.g. **Recovery needs a larger budget**. Sections: Why work paused; what is already safe; proposed worker/action; added permission or estimated spend; exact bound snapshot; expiry; alternatives.

Primary button is explicit: **Approve this recovery**. Secondary: **Keep paused**. Never a vague OK. A changed/expired snapshot disables the old approval and explains why. An approval receipt persists in history.

### S06 - Checkpoint inspector

Show objective/version, completeness, scope, files, protected test results, failed approaches and next proposed actions. Use tabs Overview / Files / Evidence / Export. Each statement has a subtle Observed / Reported / Inferred / Verified label. File manifest displays hashes on demand, not 64 characters dominating every row.

Export review flags exclusions. An incomplete checkpoint has **Not eligible for automatic recovery**, not a reassuring green success banner. Import is quarantined until validation and explicit trust.

### S07 - Verification receipt

Header: **Checks passed on this snapshot** when justified. Include run, snapshot short hash, protected suite digest, verification time and criterion rows. Each row expands to exact command ID, exit code, duration and escaped output.

An agent completion claim appears separately: "Worker reported completion at ...". When checks fail: **Work needs another pass**, with direct evidence. Test tampering gets a dedicated blocked state, not normal failure.

Primary outcome: **Review changes**. Secondary: **Export patch**. Do not put a deploy/merge button here unless the explicit manual workflow is implemented and authorized.

### S08 - Connections

A restrained table displays Codex - existing login, Bedrock - region/model, last tested time, readiness and supported features. The quota panel shows actual windows and last updated time. Unknown, stale and unavailable are different states. A dollar balance is never presented as quota percentage.

Edit uses plain forms with inline validation. Removing an active provider offers drain/stop instructions. Credential values are never read back. Reconnect leads to official auth, not a password field in Dovet chat.

### S09 - Project policy

Sections: Mode; authorized workers; scope; checks; safe recovery; usage threshold; budget; data sharing; retention. Plain language precedes advanced fields. A read-only effective-policy preview shows what will be allowed. Saving produces a new version and may require approval; changes do not silently alter in-flight actions.

### S10 - History

Rows grouped by task, expandable attempts and recovery lineage. Filter verified/paused/failed/interrupted; search title/project locally. Detail includes a downloadable evidence receipt. Durations and costs always indicate measured/estimated/unknown. Do not calculate money saved without a tested counterfactual.

### S11 - Hosted demo

Visible mode tabs: **Run live demo** and **View recorded run**. Live mode explains the fixed synthetic repository, limited scope and expected costs funded by the operator. Live controls: Start demo, Interrupt this worker, Inspect checkpoint, Observe recovery. These are real requests with request IDs.

Recorded mode has a permanent **Recorded evidence** label, capture date, source commit and restart-playback control. A live failure stays a failure; do not automatically swap to replay behind the same status.

### S12 - Offline / degraded

Keep the last valid history available. State: **Local worker unavailable. Your last saved checkpoint is still available.** Never promise unsaved current work is captured. Show a reconnect/doctor path and last observation time. Prevent recovery while source/ownership is uncertain.

## 7. Interaction details

Changes arrive via authorized SSE locally and bounded polling for the cloud demo. Reconnection uses last event sequence without duplicate rows. Do not steal focus on background events. Announce important status changes through restrained aria-live regions. Pending mutations show their actual operation state, not optimistic success.

Toast examples: "Checkpoint requested" -> later "Checkpoint saved" only after validation. Approval updates appear in the decision list. Status transitions may use 120-180 ms opacity/position changes; no perpetual pulses or scrolling marquees. Honor reduced motion.

Keyboard: Cmd/Ctrl-K opens commands; Escape closes a nonblocking drawer; no global single-letter destructive shortcuts. All dialogs restore focus and trap it correctly. Show tooltips on keyboard focus as well as hover.

## 8. Accessibility and visual QA

Verify ordinary text contrast >=4.5:1 and nontext controls >=3:1. Use visible focus, labels, aria descriptions for errors, semantic tables/lists and status text. Minimum effective pointer target 44 px where practical. Test at 200% zoom, 390/768/1440 px widths and system dark mode. Code/diff views must remain copyable/selectable.

Initial release uses light mode plus a complete tested dark token set, not automatic inversion. Every empty, loading, error, denied, expired, offline and partial-data state must be designed. No fake skeletons held for aesthetic delay.

## 9. Research references, not assets

The inspected Linear issue screen uses a quiet navigation rail, clear main reading column and secondary properties panel. Borrow that information hierarchy, not its branding or exact composition:
https://mobbin.com/screens/cef36326-d8ec-4c6f-acd4-a9f1e1060d33

The inspected Vercel section separates explanatory copy from two short actions with ample whitespace. Borrow the action hierarchy, not its gradient treatment or text:
https://mobbin.com/sites/sections/62c13ac6-ec58-49af-9507-9f059e91a4fc

Mobbin reference screenshots are not redistribution assets. Do not include them in the public product or repository. Dovet's evidence-rail pattern, palette, layout and original vector mark are its own implementation.
