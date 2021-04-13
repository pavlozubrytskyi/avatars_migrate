#!/usr/bin/env python

import os
import psycopg2
import boto3
import re
from multiprocessing.pool import ThreadPool

# S3 legacy bucket name to use. It should exist and be accessible to your AWS credentials
S3_LEGACY_BUCKET_NAME = os.getenv(
                                  'S3_LEGACY_BUCKET_NAME',
                                  'sketch-legacy-s3'
                                 )

# S3 production bucket name to use. It should exist and be accessible to your AWS credentials
S3_PRODUCTION_BUCKET_NAME = os.getenv(
                                      'S3_PRODUCTION_BUCKET_NAME',
                                      'sketch-production-s3'
                                     )

# S3 connection details
S3_LEGACY_ENDPOINT_URL = os.getenv(
                                   'S3_LEGACY_ENDPOINT_URL',
                                   'https://sketch-legacy-s3.s3.amazonaws.com'
                                  )

S3_PRODUCTION_ENDPOINT_URL = os.getenv(
                                       'S3_PRODUCTION_ENDPOINT_URL',
                                       'https://sketch-production-s3.s3.amazonaws.com'
                                       )

# AWS creds
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', 'minioadmin')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', 'minioadmin')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

# DB connection
try:
    client = boto3.client('rds')
    instances = client.describe_db_instances()
    rds_host_endpoint = instances['DBInstances'][0]['Endpoint']['Address']
    DB_CONN_STRING = os.getenv(
                               'DB_CONN_STRING',
                               'postgres://sketch_user:YourPwdShouldBeLongAndSecure!@'
                                + rds_host_endpoint + '/sketchdb'
                              )
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

# Update lecagy item paths in S3 producton and clean up
def move_legacy_names_prodS3(connection, src_bucket, dst_bucket):
    try:
        cur = connection.cursor()
        s3 = boto3.resource('s3')
        pool = ThreadPool(processes=8)
        cpy_list = []
        prefix_old = "{}/image/".format(src_bucket)
        prefix_new = "{}/avatar/".format(dst_bucket)
        src_s3 = s3.Bucket(src_bucket)
        for s3_file in src_s3.objects.filter(Prefix=prefix_old).all():
            cpy_list.append(s3_file.key)
        s3 = boto3.client('s3')
        def move_mp(file_key):
            new_key = re.sub(r'%s' % prefix_old, '%s' % prefix_new, file_key)
            copy_source = {
                'Bucket': src_bucket,
                'Key': file_key
            }
            try:
                s3.copy_object(CopySource=copy_source, Bucket=dst_bucket, Key=new_key)
            except Exception as e:
                raise e
            old_db_path = S3_LEGACY_ENDPOINT_URL + '/' + file_key
            new_db_path = S3_PRODUCTION_ENDPOINT_URL + '/' + new_key
            print("UPDATE path SET = '{}' where path like '%{}%'".format(new_db_path,old_db_path))
            try:
                cur.execute("UPDATE avatars SET path = '{}' where path like '%{}%'".format(new_db_path,old_db_path))
            except Exception as e:
                raise e
            try:
                connection.commit()
            except Exception as e:
                raise e
            try:
                s3.delete_object(Bucket=src_bucket,Key=file_key)
            except Exception as e:
                raise e
            return new_key
        pool.map(move_mp,cpy_list)
    except Exception as e:
        raise e

def main():
    # Connect to rds DB
        try:
            db_conn = psycopg2.connect(DB_CONN_STRING)
        except Exception as e:
            raise e

    # Move legacy avarars to production and update DB records
        try:
            legacy_avatar_ids = get_legacy_db_records(db_conn,
                                                        S3_LEGACY_BUCKET_NAME,
                                                        S3_PRODUCTION_BUCKET_NAME,
                                                        S3_LEGACY_ENDPOINT_URL
                                                        + '/' +
                                                        S3_LEGACY_BUCKET_NAME
                                                        )
            legacy_avatars_count = len(legacy_avatar_ids)
            if legacy_avatars_count != 0:
                print("There are {} legacy avatars left to migrate".format(legacy_avatars_count))
                move_legacy_names_prodS3(db_conn,S3_LEGACY_BUCKET_NAME,S3_PRODUCTION_BUCKET_NAME)
            else:
                print("All legacy avatars have been already migrated!")
        except Exception as e:
            raise e

if __name__ == "__main__":
    main()
