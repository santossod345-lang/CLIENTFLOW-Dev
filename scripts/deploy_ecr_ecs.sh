#!/usr/bin/env bash
set -euo pipefail

# Usage: export AWS_* and other env vars, then run: ./scripts/deploy_ecr_ecs.sh

# Ensure required env vars are set: AWS_REGION ECR_REPOSITORY AWS_ACCOUNT_ID ECS_CLUSTER ECS_SERVICE TASK_EXEC_ROLE_ARN TASK_ROLE_ARN CONTAINER_NAME CONTAINER_PORT

AWS_REGION=${AWS_REGION:-}
AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID:-}
ECR_REPOSITORY=${ECR_REPOSITORY:-}
ECS_CLUSTER=${ECS_CLUSTER:-}
ECS_SERVICE=${ECS_SERVICE:-}
TASK_EXEC_ROLE_ARN=${TASK_EXEC_ROLE_ARN:-}
TASK_ROLE_ARN=${TASK_ROLE_ARN:-}
CONTAINER_NAME=${CONTAINER_NAME:-clientflow}
CONTAINER_PORT=${CONTAINER_PORT:-8000}

if [ -z "$AWS_REGION" ] || [ -z "$ECR_REPOSITORY" ] || [ -z "$AWS_ACCOUNT_ID" ]; then
  echo "Missing required env vars. See .env.example"
  exit 1
fi

IMAGE_TAG=$(git rev-parse --short HEAD)
REPO_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY"

# Build and push
docker build -t $REPO_URI:$IMAGE_TAG .
aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION || true
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker push $REPO_URI:$IMAGE_TAG

# Prepare task definition
mkdir -p ecs
sed -e "s|__IMAGE_URI__|$REPO_URI:$IMAGE_TAG|g" \
    -e "s|__EXEC_ROLE__|$TASK_EXEC_ROLE_ARN|g" \
    -e "s|__TASK_ROLE__|$TASK_ROLE_ARN|g" \
    -e "s|__CONTAINER_NAME__|$CONTAINER_NAME|g" \
    -e "s|__CONTAINER_PORT__|$CONTAINER_PORT|g" \
    -e "s|__AWS_REGION__|$AWS_REGION|g" \
    ecs/taskdef.template.json > ecs/taskdef.json

aws ecs register-task-definition --cli-input-json file://ecs/taskdef.json --region $AWS_REGION
aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --force-new-deployment --region $AWS_REGION

echo "Deployed $REPO_URI:$IMAGE_TAG to $ECS_CLUSTER/$ECS_SERVICE"
