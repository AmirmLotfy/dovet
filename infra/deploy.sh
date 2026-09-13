#!/bin/sh
set -eu

if [ "${DOVET_APPLY:-}" != "approved" ]; then
  echo "BLOCKED: set DOVET_APPLY=approved only after owner review of the concrete change set." >&2
  exit 3
fi
if [ "$#" -ne 1 ]; then
  echo "usage: infra/deploy.sh <exact-approved-model-arn>" >&2
  exit 2
fi

model_arn=$1
stack_name=${DOVET_STACK_NAME:-dovet-demo}

aws cloudformation deploy \
  --stack-name "$stack_name" \
  --template-file infra/template.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides "AllowedModelArn=$model_arn" \
  --no-fail-on-empty-changeset
