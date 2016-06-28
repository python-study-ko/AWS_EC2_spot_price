import datetime
from pprint import pprint

import boto3

from tasks.celery_settings import DEFAULT_REGION
from tasks.celeryapp import celeryapp


@celeryapp.task
def crawl_region():  # once a day
    client = boto3.client('ec2', region_name=DEFAULT_REGION)
    region_dict = client.describe_regions()
    pprint(region_dict)
    # TODO: save data to DB


@celeryapp.task
def crawl_az(region_list):     # once a day
    # TODO: get region_list from DB
    result_dict = dict()
    for region in region_list:
        client = boto3.client('ec2', region_name=region)
        az_dict = client.describe_availability_zones()
        result_dict[region] = az_dict
    pprint(result_dict)
    # TODO: save data to DB


@celeryapp.task
def crawl_spot_price(region, epoch):     # every minute triggered by ignite_crawler
    end = datetime.datetime.strptime(epoch, '%Y-%m-%dT%H:%M:%S')
    start = end - datetime.timedelta(minutes=1)
    filters = [{"Name": "timestamp", "Values": [start.strftime('%Y-%m-%dT%H:%M:*')]}]

    client = boto3.client('ec2', region_name=region)
    price_history = client.describe_spot_price_history(StartTime=start, EndTime=end, Filters=filters)
    pprint(price_history)
    # TODO: update product description, instance type
    # TODO: save data to DB


@celeryapp.task
def ignite_crawler(region_list):
    # TODO: get region_list from DB
    epoch = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    for region in region_list:
        crawl_spot_price.apply_async(args=[region, epoch], queue='crawl')
    print("Ignition")
