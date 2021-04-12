#!/usr/bin/env python

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


# Get legacy items to copy
def list_to_copy(src_bucket, dst_bucket):
    try:
        s3 = boto3.resource('s3')
        src_bucket, dst_bucket = s3.Bucket(src_bucket), s3.Bucket(dst_bucket)
        src_list, dst_list = [], []
        for s3_file in src_bucket.objects.all():
            src_list.append(s3_file.key)
        for s3_file in dst_bucket.objects.all():
            dst_list.append(s3_file.key)
        return list(set(src_list).difference(dst_list))
    except Exception as e:
        raise e

# Copy legacy items as is from legacy to prod S3
def copy_files_to_prodS3(src_bucket, dst_bucket, cpy_list):
    try:
        s3 = boto3.client('s3')
        pool = ThreadPool(processes=16)
        def copy_mp(file):
            copy_source = {
                'Bucket': src_bucket,
                'Key': file
            }
            s3.copy_object(CopySource=copy_source, Bucket=dst_bucket, Key=file)
            return file
        pool.map(copy_mp, cpy_list)
    except Exception as e:
        raise e

# Get list of legacy db records
def get_legacy_db_records(connection,src_bucket, dst_bucket,path=None):
    try:
        cur = connection.cursor()
        legacy_avatars = cur.execute("select * from avatars where path like '%{}%'".format(path))
        legacy_avatars_ids = [ id for id,_ in cur.fetchall() ]
        return legacy_avatars_ids
    except Exception as e:
        raise e


if __name__ == "__main__":

# Connect to rds DB
    try:
        db_conn = psycopg2.connect(DB_CONN_STRING)
    except Exception as e:
        raise e

# List and copy legacy avatars to move
    try:
        l = list_to_copy(S3_LEGACY_BUCKET_NAME,S3_PRODUCTION_BUCKET_NAME)
        if len(l) != 0:
            copy_files_to_prodS3(S3_LEGACY_BUCKET_NAME,S3_PRODUCTION_BUCKET_NAME,l)
        else:
            print("No legacy avatars to migrate!")
    except Exception as e:
        raise e
