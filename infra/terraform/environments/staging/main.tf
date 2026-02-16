// Staging environment wiring example for AWS
module "vpc" {
  source = "../../modules/vpc"
  name   = "clientflow-staging"
  tags   = { Environment = "staging" }
}

module "db" {
  source = "../../modules/rds"
  name   = "clientflow"
  environment = "staging"
  username = "cf_staging"
  password = var.db_password
  subnet_ids = module.vpc.private_subnet_ids
  security_group_ids = []
  tags = { Environment = "staging" }
}
// Staging environment - minimal example
module "example" {
  source = "../../modules/example-module"
  environment = "staging"
}
