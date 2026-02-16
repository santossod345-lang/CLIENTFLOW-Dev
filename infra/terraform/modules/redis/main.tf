// Minimal ElastiCache Redis module (placeholder)
variable "cluster_id" {
  type = string
}

variable "node_type" {
  type    = string
  default = "cache.t3.micro"
}

variable "num_cache_nodes" {
  type    = number
  default = 1
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id          = var.cluster_id
  replication_group_description = "ClientFlow Redis replication group"
  node_type                     = var.node_type
  number_cache_clusters         = var.num_cache_nodes
  automatic_failover_enabled    = false
  engine                        = "redis"
  engine_version                = "6.x"
}

output "primary_endpoint_address" {
  value = aws_elasticache_replication_group.this.primary_endpoint_address
}
