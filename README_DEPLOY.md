Deployment guide (ECS / ECR)

1. Create AWS resources (ECR repository, ECS cluster, service) or reuse existing.
2. Create GitHub repository secrets:
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_ACCOUNT_ID`
   - `ECR_REPOSITORY` (name)
   - `ECS_CLUSTER`, `ECS_SERVICE`
   - `TASK_EXEC_ROLE_ARN`, `TASK_ROLE_ARN`, `CONTAINER_NAME`, `CONTAINER_PORT`
3. The workflow `.github/workflows/deploy-ecs.yml` will build and push image on push to `main` and register a new task definition and update the service.
4. For local deploy, populate environment from `.env.example` and run:

```bash
export $(cat .env.example | xargs)
./scripts/deploy_ecr_ecs.sh
```

Notes:
- The task definition template is at `ecs/taskdef.template.json` and contains placeholders replaced by the workflow or script.
- Ensure your ECS task execution role has permissions for ECR pull and CloudWatch Logs.

Snapshot and migrations safety
- You can configure automatic RDS snapshot before migrations by setting the GitHub Secret `RDS_INSTANCE_ID` with your RDS instance identifier. The deploy workflow will create a snapshot and wait until it's available before running `alembic upgrade head`.
- Required secrets to enable migrations and snapshot steps: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and optionally `RDS_INSTANCE_ID` for snapshot.
- Important: the GitHub Actions runner must have network access to the RDS instance (use self-hosted runner in VPC or use CI that runs in the same AWS account/VPC). Alternatively run migrations from a maintenance container in the cluster.

Rollback support
- During each deploy the workflow now captures the current ECS service description (including `taskDefinition`) and uploads it as an artifact named `previous-ecs-taskdef-<run_id>` — you can download that artifact from the Actions run and find the previous `taskDefinitionArn` to rollback.
- There's also a manual workflow `.github/workflows/rollback-ecs.yml` that accepts a `task_definition_arn` and updates the service to use it.
- For local rollback you can use `scripts/rollback_using_arn.sh <cluster> <service> <task_definition_arn> [region]`.


