output "primary_endpoint_address" {
  description = "Primary endpoint address for Redis"
  value       = aws_elasticache_replication_group.this.primary_endpoint_address
}
