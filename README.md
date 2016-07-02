# AWS_EC2_spot_price

## Environment / Spicification

- ubuntu 14.04 LTS on AWS EC2
- postgresql 9.3 on AWS RDS
- AWS DynamoDB
- python 3.4

## Pre-requirements for Service

- sudo apt-get update && sudo apt-get -y upgrade
- sudo apt-get install postgresql postgresql-server-dev-9.3 python3-dev rabbitmq-server python3-pip libxml2-dev libxslt-dev
- sudo pip install virtualenv

## Requirements

- virtualenv -p python3 .venv
- . .venv/bin/activate
- pip3 install -r requirements.txt

## Important Packages

- boto3
- flask
- sqlalchemy
- celery
