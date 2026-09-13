"""Authenticated HTTP-compatible AgentCore Runtime entry point."""

from __future__ import annotations

import asyncio
import os
from typing import Any

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from .agent import EvidenceEnvelope, build_agent, recommend

app = BedrockAgentCoreApp()


@app.entrypoint
def decide(payload: dict[str, Any]) -> dict[str, Any]:
    model_id = os.environ.get("DOVET_BEDROCK_MODEL_ID")
    region = os.environ.get("AWS_REGION")
    if not model_id or not region:
        return {"status": "blocked", "code": "PROVIDER_UNAVAILABLE"}
    records = payload.get("evidence")
    prompt = payload.get("prompt")
    if not isinstance(records, dict) or not isinstance(prompt, str):
        return {"status": "blocked", "code": "VALIDATION_ERROR"}
    agent = build_agent(model_id=model_id, region=region, evidence=EvidenceEnvelope(records))
    decision = asyncio.run(recommend(agent, prompt))
    return {"status": "proposed", "decision": decision.model_dump(by_alias=True, mode="json")}


def main() -> None:
    app.run()
