# Dovet architecture

![Dovet architecture](architecture.svg)

The local daemon is the durability boundary. The Codex plugin and console processes may
exit without taking the ledger or immutable artifacts with them. Automatic interruption and
handoff apply only to managed workers whose process identity Dovet recorded.

The Strands supervisor receives a bounded evidence envelope and returns a typed recommendation.
Approval, budget, policy, snapshot, and lease checks run in deterministic local code. The AWS
infrastructure is deployable and validates as CloudFormation, while live Bedrock invocation and
AgentCore deployment remain blocked until a least-privilege role is authorized and proves one
successful request.

The public site and recorded replay cannot call the local daemon. A future live hosted demo accepts
only fixed synthetic fixtures and runs generated fixture code in a permission-minimized AgentCore
Code Interpreter session.
