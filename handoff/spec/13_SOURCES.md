# 13 - Source ledger and capability provenance

Checked on **2026-09-13**. These are references for facts and API verification, not a guarantee that every proposed integration has been implemented. Recheck versioned SDK/API behavior in the actual build environment and recheck competition amendments before submission.

Most of this handoff consists of original architecture/product decisions. Labels such as G3, DovetCheckpoint/1, Dovet API endpoints, layout dimensions and operational thresholds are design choices, not claims that a vendor already supplies those features.

## Competition

**S01 - Hackathon overview**  
https://agentsforhumans.devpost.com/  
Audience/tracks, deadline and submission summary. Professional Agents is the chosen fit for developer work; a prize outcome is not predictable from the rubric.

**S02 - Official rules and FAQ**  
https://agentsforhumans.devpost.com/rules  
https://agentsforhumans.devpost.com/details/faqs  
Required technology, submission/publication obligations, AI-assistant allowance, judging/access window, optional bonus and owner's eligibility/IP obligations. Rules take priority over this digest.

**S03 - Current resources**  
https://agentsforhumans.devpost.com/resources  
The page explicitly reports promotional credit exhaustion. Do not rely on an older FAQ invitation to request credits.

## Codex

**S04 - Official app-server protocol**  
https://developers.openai.com/codex/app-server  
https://learn.chatgpt.com/docs/app-server  
Owned thread/turn interfaces, supported schema generation and authenticated rate-limit reads/updates. This is not proof that a plugin can attach to every existing Desktop conversation. Capability-check the installed version. Production use of under-development plugin control methods is not part of this plan.

**S05 - Official Codex SDK**  
https://developers.openai.com/codex/sdk  
https://learn.chatgpt.com/docs/codex-sdk  
Use the documented stable SDK/runtime interface and verify the actual Python/TypeScript release selected. SDK support does not imply privileged Desktop UI control.

**S06 - Plugin packaging**  
https://developers.openai.com/plugins/build/plugins  
Current portable plugin structure, OpenAI extensions and legacy compatibility. Generate/validate the manifest against current guidance rather than hard-coding an old tutorial. Local distribution and a public directory listing are different deliverables.

## Strands and Bedrock

**S07 - Strands quickstart**  
https://strandsagents.com/docs/user-guide/quickstart/overview/  
SDK installation and agent concepts; pin the versions actually tested.

**S08 - Structured output**  
https://strandsagents.com/docs/user-guide/concepts/agents/structured-output/  
Use the current typed-output invocation contract, not a deprecated convenience method.

**S09 - Agent loop**  
https://strandsagents.com/docs/user-guide/concepts/agents/agent-loop/  
Tool/agent-loop behavior and controls. Dovet adds its own external wall-time, attempt and spending guards.

**S10 - Interrupts**  
https://strandsagents.com/docs/user-guide/concepts/interrupts/  
Human-interruption mechanisms; a Dovet approval ledger remains a separate security requirement.

**S11 - Bedrock model discovery**  
https://docs.aws.amazon.com/bedrock/latest/userguide/models.html  
https://docs.aws.amazon.com/bedrock/latest/userguide/models-get-info.html  
Discover model availability/capabilities and verify actual account access. No model name, region or price is presumed from memory.

**S12 - Existing ACP terminology**  
https://agentclientprotocol.com/get-started/introduction  
ACP already refers to Agent Client Protocol. The project therefore uses DovetCheckpoint/1 rather than claiming a conflicting new standard.

**S13 - AgentCore current CLI deployment**  
https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html  
Current CLI prerequisites and deployment path. Validate the installed CLI family before following commands.

**S14 - AgentCore asynchronous work**  
https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-long-run.html  
Managed async task lifecycle/health behavior. External durable state is a Dovet architectural requirement, not a claim that a background thread persists forever.

**S19 - AgentCore Code Interpreter isolation and file operations**  
https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-resource-management.html  
https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-file-operations.html  
https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-execute-code.html  
Cloud code execution can use dedicated sessions. Sandbox network mode is not a promise of zero AWS network access; restrict execution-role permissions and verify the actual behavior. The public fixture must not execute generated code in the supervisor's credentialed runtime.

## Video and publication

**S15 - Playwright recordings**  
https://playwright.dev/docs/videos  
Explicit recording dimensions and closing the browser context to finalize files.

**S16 - Amazon Polly narration/timing**  
https://docs.aws.amazon.com/polly/latest/APIReference/API_DescribeVoices.html  
https://docs.aws.amazon.com/polly/latest/dg/speechmarks.html  
Discover supported voices/engines; generate aligned speech/timing with an authorized account.

**S17 - YouTube upload behavior**  
https://developers.google.com/youtube/v3/docs/videos/insert  
https://developers.google.com/youtube/v3/docs/videos  
Uploads from qualifying unaudited API projects can be restricted to private visibility. A new API project is not guaranteed to produce a public submission video; use the legitimate Studio flow when needed.

## Website

**S18 - Vercel deployment/domains**  
https://vercel.com/docs/projects/deploy-from-cli  
https://vercel.com/docs/domains/set-up-custom-domain  
https://vercel.com/docs/cli  
Use actual project-specific DNS/ownership instructions and verify the deployed URL. Naming a domain does not establish availability or deployment.

## Visual reference research

These references were retrieved with Mobbin and their returned images were inspected. They inform layout principles, not source-code or artwork reuse.

**D01 - Linear issue detail**  
https://mobbin.com/screens/cef36326-d8ec-4c6f-acd4-a9f1e1060d33  
Observed: narrow navigation, a central issue/activity area and a properties column. Dovet adapts the readable information hierarchy to evidence and recovery decisions, not the product's branding.

**D02 - Vercel call-to-action/footer section**  
https://mobbin.com/sites/sections/62c13ac6-ec58-49af-9507-9f059e91a4fc  
Observed: clear typographic CTA, restrained actions and a spacious footer. This was not a complete homepage/hero audit.

No reference screenshots or font binaries are redistributed in this pack.

## Unverified matters to resolve in the real environment

Domain registration/trademark clearance; actual AWS model access and pricing; installed Codex plugin/runtime compatibility; specific Mac service behavior; cloud execution sandbox configuration; permission to publish source/video; authenticated YouTube/Devpost access; current submission-field shape; and whether the completed application meets the specified performance targets.
