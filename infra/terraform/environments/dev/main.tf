// Dev environment: provision a small Redis for development using the redis module
provider "aws" {
  region = var.aws_region
}

module "redis" {
  source = "../../modules/redis"
  cluster_id = "clientflow-dev-redis"
  node_type = "cache.t3.micro"
  num_cache_nodes = 1
}

output "redis_primary_endpoint" {
  value = module.redis.primary_endpoint_address
}
// Dev environment wiring example for AWS
module "vpc" {
  source = "../../modules/vpc"
  name   = "clientflow-dev"
  tags   = { Environment = "dev" }
}

module "db" {
  source = "../../modules/rds"
  name   = "clientflow"
  environment = "dev"
  username = "cf_dev"
  password = var.db_password
  subnet_ids = module.vpc.private_subnet_ids
  security_group_ids = []
  tags = { Environment = "dev" }
}
// Dev environment - minimal example
module "example" {
  source = "../../modules/example-module"
  environment = "dev"
}
