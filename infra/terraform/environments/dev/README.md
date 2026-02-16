Dev environment for Terraform

To provision the Redis dev instance (ElastiCache), set your AWS credentials and run from this folder:

```bash
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export TF_VAR_aws_region=us-east-1
terraform init
terraform apply -var-file=terraform.tfvars.example
```

The module will output `redis_primary_endpoint` which can be used to form `REDIS_URL`.
