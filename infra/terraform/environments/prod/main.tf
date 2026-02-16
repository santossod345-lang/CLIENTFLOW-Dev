// Prod environment wiring example for AWS
module "vpc" {
  source = "../../modules/vpc"
  name   = "clientflow-prod"
  tags   = { Environment = "prod" }
}

module "db" {
  source = "../../modules/rds"
  name   = "clientflow"
  environment = "prod"
  username = "cf_prod"
  password = var.db_password
  subnet_ids = module.vpc.private_subnet_ids
  security_group_ids = []
  tags = { Environment = "prod" }
}
// Prod environment - minimal example
module "example" {
  source = "../../modules/example-module"
  environment = "prod"
}
