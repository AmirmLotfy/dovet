# Dovet AWS infrastructure

This stack creates private, encrypted evidence storage, a durable demo ledger, bounded log
retention, and two separate AgentCore roles. The runtime role can invoke exactly one model ARN.
The Code Interpreter role can read only the released synthetic fixture and protected tests and
can write only candidate artifacts. Neither role exposes a route to a local machine.

The stack deliberately does not create a public API or an AgentCore runtime until a model
invocation conformance probe succeeds. Nova Micro currently reports `NOT_AUTHORIZED` for this
account even though its region, entitlement, and agreement are available. The owner completed the
console first-use action; the provider still denies both playground and API inference. AWS Support
now has the exact authorization, request, root-account, and zero-quota evidence. A read-only sweep
found zero authorized alternatives among all 89 discovered text models in `us-east-1`.
`infra/deploy.sh` refuses to execute without an explicit
`DOVET_APPLY=approved` environment value. Generate and inspect a CloudFormation change set first.

```sh
aws cloudformation validate-template --template-body file://infra/template.yaml
infra/plan.sh arn:aws:bedrock:REGION:ACCOUNT:inference-profile/APPROVED_PROFILE
# Review the change set and estimated service pricing, then:
DOVET_APPLY=approved infra/deploy.sh arn:aws:bedrock:REGION:ACCOUNT:inference-profile/APPROVED_PROFILE
```

AgentCore direct-code deployment is packaged as a Linux arm64 ZIP by
`python infra/package_runtime.py`. Deployment requires the stack's bucket and runtime-role
outputs, an exact model ID that passed live invocation, and a reviewed `create-agent-runtime`
request. The current account probe is recorded as BLOCKED, so no runtime has been deployed.

The S3 bucket and DynamoDB table use retained deletion policies. Teardown therefore preserves
evidence by design; an owner must review and explicitly remove retained data later.
