#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: infra/plan.sh <exact-approved-model-arn>" >&2
  exit 2
fi

model_arn=$1
stack_name=${DOVET_STACK_NAME:-dovet-demo}
change_set="dovet-plan-$(date -u +%Y%m%dT%H%M%SZ)"

aws cloudformation create-change-set \
  --stack-name "$stack_name" \
  --change-set-name "$change_set" \
  --change-set-type CREATE \
  --template-body file://infra/template.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters "ParameterKey=AllowedModelArn,ParameterValue=$model_arn" \
  --description "Dovet review-only infrastructure plan"

echo "Created review-only change set $change_set for $stack_name. It has not been executed."
