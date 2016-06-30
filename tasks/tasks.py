import datetime
from pprint import pprint
import logging

import boto3

from tasks.celery_settings import DEFAULT_REGION
from tasks.celeryapp import celeryapp
from gbl.models.aws import Region, AvailabilityZone, Instance, Product, SpotPrice
from gbl.common import sess, sentry


@celeryapp.task
def crawl_region():  # once a day
    client = boto3.client('ec2', region_name=DEFAULT_REGION)
    region_list = client.describe_regions()['Regions']
    prev_region = dict(sess.query(Region.name, Region).all())
    new_region_list = []
    for region_info in region_list:
        if region_info['RegionName'] in prev_region:
            new_region = prev_region[region_info['RegionName']]
        else:
            new_region = Region(region_info['RegionName'])
        new_region.endpoint = region_info['Endpoint']
        new_region_list.append(new_region)
    sess.add_all(new_region_list)
    try:
        sess.commit()
        logging.log(logging.INFO, 'Region Done')
    except:
        sess.rollback()
        sentry.captureException()
        logging.log(logging.CRITICAL, 'Region Error')


@celeryapp.task
def crawl_az():     # once a day
    region_list = sess.query(Region).all()
    prev_az = dict(sess.query(AvailabilityZone.name, AvailabilityZone).all())
    new_az_list = []

    for region in region_list:
        client = boto3.client('ec2', region_name=region.name)
        az_dict = client.describe_availability_zones()

        for az_info in az_dict['AvailabilityZones']:
            if az_info['ZoneName'] in prev_az:
                new_az = prev_az[az_info['ZoneName']]
                new_az.region = region
            else:
                new_az = AvailabilityZone(region.id, az_info['ZoneName'])
            new_az_list.append(new_az)
    sess.add_all(new_az_list)
    try:
        sess.commit()
        logging.log(logging.INFO, 'AZ Done')
    except:
        sess.rollback()
        sentry.captureException()
        logging.log(logging.CRITICAL, 'AZ Error')


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
