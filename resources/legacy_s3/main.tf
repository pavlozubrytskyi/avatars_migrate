module "s3-bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"

  bucket = "sketch-legacy-s3"
  create_bucket = true
  acl = "public-read-write"
  force_destroy = true
}

output "bucket_endpoint" {
  value = module.s3-bucket.this_s3_bucket_bucket_domain_name
}

output "bucket_name" {
  value = module.s3-bucket.this_s3_bucket_id
}
