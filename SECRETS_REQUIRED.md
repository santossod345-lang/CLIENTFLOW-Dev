Secrets and repository vars required to run workflows and deploy ClientFlow

Add these to repository Settings → Secrets and variables → Actions before running workflows.

Required secrets (minimum):

- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- AWS_REGION
- AWS_ACCOUNT_ID
- ECR_REPOSITORY
- ECS_CLUSTER
- ECS_SERVICE
- TASK_EXEC_ROLE_ARN
- TASK_ROLE_ARN
- CONTAINER_NAME
- CONTAINER_PORT
- GITHUB_TOKEN (provided by GitHub automatically but listed for awareness)

Optional (only if DB migrations / snapshots run):

- POSTGRES_HOST
- POSTGRES_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- RDS_INSTANCE_ID

How to set:

1. Go to repository Settings → Secrets and variables → Actions
2. Click `New repository secret` and add each key/value
3. For organization-wide variables use repo or organization variables as needed
