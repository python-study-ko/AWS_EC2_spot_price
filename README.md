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
- for convenient develop, recommend `pip3 install ipython` to use IPython 5.0

## Server Settings
First, copy gbl/config.cfg.example to gbl/config.cfg and fill config

### 1. Crawler
copy aws_celery.conf.example to aws_celery.conf and fill config

symbolic link aws_celery.conf into /etc/init

$ sudo initctl reload-configuration

$ sudo service aws_celery restart

(optional) $ sudo service aws_celery status to check status

### 2. Web Server
copy aws_web.ini.example to aws_web.ini and fill config

copy aws_web.conf.example to aws_web.conf and fill config

symbolic link aws_celery.conf into /etc/init

$ sudo initctl reload-configuration

$ sudo service aws_web restart

(optional) $ sudo service aws_web status to check status
