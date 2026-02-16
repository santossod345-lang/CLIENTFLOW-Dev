terraform {
  required_version = ">= 1.4.0"
  # Configure backend (example S3) here when ready:
  # backend "s3" {
  #   bucket = "your-terraform-state-bucket"
  #   key = "clientflow/terraform.tfstate"
  #   region = "us-east-1"
  # }
}

# Providers: uncomment and configure the provider you will use (AWS/GCP/Azure)
# provider "aws" {
#   region = var.aws_region
# }

locals {
  project = "clientflow"
}

output "project" {
  value = local.project
}
