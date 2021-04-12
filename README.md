**Task description**

Can be found here [TASK_DESCRIPTION.md](TASK_DESCRIPTION.md)

**Task comments**

Comments from my side [TASK_DESCRIPTION_COMMENTS.md](TASK_DESCRIPTION_COMMENTS.md)

**Run required packages setup to install dependencies (Ubuntu 18.04)**

```
sudo apt install -y postgresql-common libpq-dev postgresql-client python3-pip wget unzip; \
pip3 install --upgrade pip --user; \
pip3 install psycopg2 setuptools boto3 --user ; \
wget -q -O tmp.zip http://releases.hashicorp.com/terraform/0.14.10/terraform_0.14.10_linux_amd64.zip && \
unzip tmp.zip && rm tmp.zip && \
mkdir -p ~/.terraform && mv ./terraform ~/.terraform/ && \
export PATH="$PATH:$HOME/.terraform" && \
echo 'export PATH="$PATH:$HOME/.terraform"' >> ~/.bashrc
```

### Next set of steps have to be performed from the root of this git repo

**1. Download or clone this repository**

```
wget https://github.com/pavlozubrytskyi/avatars_migrate/archive/refs/tags/v1.tar.gz && \
tar -xzvf v1.tar.gz
```

```
git clone https://github.com/pavlozubrytskyi/avatars_migrate.git
```

**2. Change directory to avatars_migrate script**

```
cd avatars_migrate || cd avatars_migrate_v1
```

**3. Setup your AWS credentials (keys are not active, filled out for example)**

```
cat > aws_creds.sh <<EOF
export AWS_ACCESS_KEY_ID="ADASFLKJOHIGHIHKJ7797"
export AWS_SECRET_ACCESS_KEY="Kmk[m{#QRP[kp[lk[pko[KQ#]pk]p"
export AWS_DEFAULT_REGION="eu-central-1"
EOF
```

**4. Create resources for testing**

```
source aws_creds.sh; \
( cd resources/rds-postgres/; terraform init; terraform apply -auto-approve; ); \
( cd resources/legacy_s3/; terraform init; terraform apply -auto-approve; ); \
( cd resources/production_s3/; terraform init; terraform apply -auto-approve; )
```

**5. Configure the environment (your script with a couple of modifications)**

```
source aws_creds.sh; python3 setup_environment.py
```

**6. Run the migration script**

```
source aws_creds.sh; python3 migrate_avatars.py
```


**7. Destroy resources after testing**

```
source aws_creds.sh; \
( cd resources/rds-postgres/; terraform destroy -auto-approve; ); \
( cd resources/legacy_s3/; terraform destroy -auto-approve; ); \
( cd resources/production_s3/; terraform destroy -auto-approve; )
```
