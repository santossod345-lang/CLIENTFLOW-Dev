variable "environment" {
  description = "Deployment environment (dev|staging|prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region (if using AWS provider)"
  type        = string
  default     = "us-east-1"
}
