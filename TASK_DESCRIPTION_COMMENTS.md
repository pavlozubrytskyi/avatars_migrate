>If you want, you can use the provided database schema and seeding script (python 3, requires psycopg2-binary and boto3) that will generate both the database rows and the S3 objects for the legacy assets, in any existing PostgreSQL database and S3 bucket, so you can focus on your program instead of in setting everything up.

I've used your schema and seeding script with a few quick and dirty modifications which added the ability to seed production s3 and create mixed paths in the database and also made this script indempotent.

> - The program to be written in a real programming language like Python, Ruby, Go, Elixir, etc… Please, avoid shell scripting or similar. We don't expect a code masterpiece but we expect clean code that is easy to understand and modify without major refactors.

Chosen language for the migration script is Pyhon3.*

>- The program to run in a UNIX-like environment,

In my case it was Ubuntu 18.04, but it's possible to wrap everyting up in a docker container and run on any current Linux distro

>- Able to be tested and run with minimal setup/configuration

The testing environment if given the correct AWS credentials can be brought up and brought down with two one liners provided in the README.md

>- Your program to handle most common problems. It should not crash if something unexpected happens and it should be able to resume if it stops at the middle.

The migration script can resume on unprocessed files

>- The program to be fast and efficient; the buckets store several millions of images, and we want to move them in the shortest time possible. We would like to have your comments about performance and scalability when you send the challenge back to us.

The migration script can run in parallellized manner and in this specific configuration it spawns 16 subprocesses to handle copy from bucket to bucket.
In real environment with millions of records i would use AWS resource inventory functionality and parse the legacy objects in order to avoid costly S3 list operations.
Then i would have used either AWS lambda functionality and queuing in order to parallellize copy objects functionality.
Or instead of lambda i could use powerful jumphost on EC2 in order to be able to use boto3 file transfer and migrate the avatars in big batch.

>- This program to be able to run in a production environment. Meaning that the information located in the database must always point to an existing PNG in S3 and not cause any service disruption.

The updates of the database are being done only as the last step of the migration.
The script is doing the migration in three steps: copy S3 legacy avatars to production S3, update legacy paths on production S3, and after successful first two steps leads the database update state in raw sql in order to hand over the responsibility of transaction to the database engine.

>- You to write a few lines explaining you development setup (how did you create or emulate the resources)

I've created three terraform configurations with simplified config and no extensive security options for the sake of simplicity.
Each configuration is based on publically available and Hashicorp supported AWS modules for terraform.
All the names and parameters are mostly static and hardcoded for the sake of simplicity.
