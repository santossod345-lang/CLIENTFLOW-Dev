variable "cluster_id" {
  description = "ElastiCache replication group id"
  type        = string
}

variable "node_type" {
  description = "Instance type for redis nodes"
  type        = string
  default     = "cache.t3.micro"
}

variable "num_cache_nodes" {
  description = "Number of cache nodes (for cluster mode disabled)"
  type        = number
  default     = 1
}
