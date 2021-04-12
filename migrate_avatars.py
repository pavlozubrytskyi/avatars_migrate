#!/usr/bin/env python

import sys
import os
import psycopg2
import boto3
import re
from multiprocessing.pool import ThreadPool


# S3 legacy bucket name to use. It should exist and be accessible to your AWS credentials
S3_LEGACY_BUCKET_NAME = os.getenv('S3_LEGACY_BUCKET_NAME', 'sketch-legacy-s3')

# S3 production bucket name to use. It should exist and be accessible to your AWS credentials
S3_PRODUCTION_BUCKET_NAME = os.getenv('S3_PRODUCTION_BUCKET_NAME', 'sketch-production-s3')

# S3 connection details
S3_LEGACY_ENDPOINT_URL = os.getenv('S3_LEGACY_ENDPOINT_URL', 'https://sketch-legacy-s3.s3.amazonaws.com')
S3_PRODUCTION_ENDPOINT_URL = os.getenv('S3_PRODUCTION_ENDPOINT_URL', 'https://sketch-production-s3.s3.amazonaws.com')

# AWS creds
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# DB connection
try:
    client = boto3.client('rds')
    instances = client.describe_db_instances()
    rds_host_endpoint = instances['DBInstances'][0]['Endpoint']['Address']
    DB_CONN_STRING = os.getenv('DB_CONN_STRING',
                                'postgres://sketch_user:YourPwdShouldBeLongAndSecure!@'
                                + rds_host_endpoint + '/sketchdb')
except Exception as e:
    raise e
