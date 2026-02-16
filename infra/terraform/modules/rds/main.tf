resource "aws_db_subnet_group" "this" {
  name       = "${var.name}-db-subnet-group"
  subnet_ids = var.subnet_ids
  tags       = var.tags
}

resource "aws_db_instance" "this" {
  identifier = "${var.name}-db-${var.environment}"
  engine            = "postgres"
  engine_version    = var.engine_version
  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage
  name              = var.db_name
  username          = var.username
  password          = var.password
  db_subnet_group_name = aws_db_subnet_group.this.name
  skip_final_snapshot = true
  publicly_accessible = false
  vpc_security_group_ids = var.security_group_ids
  tags = var.tags
}
