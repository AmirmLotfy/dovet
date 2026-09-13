"""Create a reviewed Dovet AgentCore runtime from an uploaded direct-code package."""

from __future__ import annotations

import argparse
import json
import sys
import uuid

import boto3


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--bucket", required=True)
    value.add_argument("--prefix", required=True)
    value.add_argument("--role-arn", required=True)
    value.add_argument("--model-id", required=True)
    value.add_argument("--region", default="us-east-1")
    value.add_argument("--apply", action="store_true")
    return value


def main() -> int:
    args = parser().parse_args()
    request = {
        "agentRuntimeName": "DovetRecoverySupervisor",
        "agentRuntimeArtifact": {
            "codeConfiguration": {
                "code": {"s3": {"bucket": args.bucket, "prefix": args.prefix}},
                "runtime": "PYTHON_3_12",
                "entryPoint": ["main.py"],
            }
        },
        "roleArn": args.role_arn,
        "networkConfiguration": {"networkMode": "PUBLIC"},
        "clientToken": str(uuid.uuid4()),
        "description": "Dovet typed recovery decision supervisor",
        "lifecycleConfiguration": {"idleRuntimeSessionTimeout": 300, "maxLifetime": 900},
        "environmentVariables": {
            "AWS_REGION": args.region,
            "DOVET_BEDROCK_MODEL_ID": args.model_id,
        },
        "tags": {"Project": "Dovet", "Purpose": "RecoveryDecision"},
    }
    if not args.apply:
        print(json.dumps(request, indent=2, sort_keys=True))
        print("BLOCKED: pass --apply only after IAM, model conformance and cost approval.")
        return 3
    client = boto3.client("bedrock-agentcore-control", region_name=args.region)
    response = client.create_agent_runtime(**request)
    print(
        json.dumps(
            {
                "agentRuntimeArn": response.get("agentRuntimeArn"),
                "agentRuntimeId": response.get("agentRuntimeId"),
                "status": response.get("status"),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
