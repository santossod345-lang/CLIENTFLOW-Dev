#!/usr/bin/env bash
set -euo pipefail

# Bootstrap an S3 bucket and DynamoDB table for Terraform remote state + locking.
# Usage:
#   TF_STATE_BUCKET=my-bucket-name TF_LOCK_TABLE=my-lock-table AWS_REGION=us-east-1 ./infra/bootstrap_remote_state.sh

BUCKET=${TF_STATE_BUCKET:-}
TABLE=${TF_LOCK_TABLE:-}
REGION=${AWS_REGION:-us-east-1}

if [ -z "$BUCKET" ] || [ -z "$TABLE" ]; then
  echo "Required env vars: TF_STATE_BUCKET and TF_LOCK_TABLE"
  exit 1
fi

echo "Bootstrapping S3 bucket: $BUCKET (region: $REGION)"
aws s3api head-bucket --bucket "$BUCKET" 2>/dev/null || \
  aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" --create-bucket-configuration LocationConstraint=$REGION

echo "Enabling versioning on bucket $BUCKET"
aws s3api put-bucket-versioning --bucket "$BUCKET" --versioning-configuration Status=Enabled

echo "Creating DynamoDB table for state locking: $TABLE"
aws dynamodb describe-table --table-name "$TABLE" --region "$REGION" 2>/dev/null || \
  aws dynamodb create-table --table-name "$TABLE" --attribute-definitions AttributeName=LockID,AttributeType=S --key-schema AttributeName=LockID,KeyType=HASH --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 --region "$REGION"

echo "Waiting for DynamoDB table to become ACTIVE"
aws dynamodb wait table-exists --table-name "$TABLE" --region "$REGION"

echo "Bootstrap completed. Update backend.tf in the target environment using the bucket/table names."
