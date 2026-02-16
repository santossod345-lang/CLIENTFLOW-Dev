#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 3 ]; then
  echo "Usage: $0 <cluster> <service> <task_definition_arn> [region]"
  exit 1
fi

CLUSTER=$1
SERVICE=$2
TASK_DEF_ARN=$3
REGION=${4:-us-east-1}

echo "Rolling back $CLUSTER/$SERVICE to $TASK_DEF_ARN in region $REGION"
aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" --task-definition "$TASK_DEF_ARN" --force-new-deployment --region "$REGION"
echo "Rollback requested"
