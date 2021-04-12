provider "aws" {
  region = local.region
}

locals {
  name   = "sketchdb"
  region = "eu-central-1"
  tags = {
    Owner       = "sketch"
    Environment = "production"
  }
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"

  name = local.name
  cidr = "10.99.0.0/18"

  azs              = ["${local.region}a", "${local.region}b", "${local.region}c"]
  public_subnets   = ["10.99.0.0/24", "10.99.1.0/24", "10.99.2.0/24"]
  private_subnets  = ["10.99.3.0/24", "10.99.4.0/24", "10.99.5.0/24"]
  database_subnets = ["10.99.7.0/24", "10.99.8.0/24", "10.99.9.0/24"]

  enable_dns_support = true
  enable_dns_hostnames = true

  create_database_subnet_group = true
  create_database_subnet_route_table = true
  create_database_internet_gateway_route = true

  tags = local.tags
}

module "security_group" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "~> 3"

  name        = local.name
  description = "Complete PostgreSQL example security group"
  vpc_id      = module.vpc.vpc_id

  ingress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      description = "PostgreSQL access from within VPC"
      cidr_blocks = module.vpc.vpc_cidr_block
    },
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      description = "PostgreSQL access from within VPC"
      cidr_blocks = "0.0.0.0/0"
    },
  ]

  tags = local.tags
}


module "db" {
  source  = "terraform-aws-modules/rds/aws"

  identifier = local.name

  engine               = "postgres"
  engine_version       = "10.15"
  family               = "postgres10" # DB parameter group
  major_engine_version = "10"         # DB option group
  instance_class       = "db.t2.micro"

  allocated_storage     = 5
  max_allocated_storage = 6

  name     = "sketchdb"
  username = "sketch_user"
  password = "YourPwdShouldBeLongAndSecure!"
  port     = 5432

  multi_az               = false
  subnet_ids             = module.vpc.database_subnets
  vpc_security_group_ids = [module.security_group.this_security_group_id]

  maintenance_window              = "Mon:00:00-Mon:03:00"
  backup_window                   = "03:00-06:00"

  backup_retention_period = 0
  skip_final_snapshot     = true
  deletion_protection     = false

  publicly_accessible = true
  create_db_instance = true

  parameters = [
    {
      name  = "autovacuum"
      value = 1
    },
    {
      name  = "client_encoding"
      value = "utf8"
    }
  ]

  tags = local.tags

}

output "this_db_instance_endpoint" {
  description = "The connection endpoint"
  value       = module.db.this_db_instance_endpoint
}

output "this_db_instance_db_name" {
  description = "The connection db name"
  value       = module.db.this_db_instance_name
}

output "this_db_instance_username" {
  description = "The connection username"
  value       = module.db.this_db_instance_username
}

output "this_db_instance_password" {
  description = "The connection password"
  value       = module.db.this_db_instance_password
}
