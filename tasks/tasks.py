import datetime
import logging
from pprint import pprint

import boto3

from tasks.celery_settings import DEFAULT_REGION
from tasks.celeryapp import celeryapp
from gbl.models.aws import Region, AvailabilityZone, Instance, SpotPrice
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
    finally:
        sess.remove()


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
                new_az.region_name = region.name
            else:
                new_az = AvailabilityZone(region.name, az_info['ZoneName'])
            new_az_list.append(new_az)
    sess.add_all(new_az_list)
    try:
        sess.commit()
        logging.log(logging.INFO, 'AZ Done')
    except:
        sess.rollback()
        sentry.captureException()
        logging.log(logging.CRITICAL, 'AZ Error')
    finally:
        sess.remove()


@celeryapp.task
def crawl_instance_type():  # once a day
    from bs4 import BeautifulSoup
    import requests
    import re
    url = 'http://docs.aws.amazon.com/cli/latest/reference/ec2/describe-spot-price-history.html'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    tag = soup.find(string=re.compile(r't2.micro'))
    lst = [x.strip() for x in tag.split('\n')[3:]]
    prev_instance = dict(sess.query(Instance.type, Instance).all())
    for instance in lst:
        if instance not in prev_instance:
            sess.add(Instance(instance))
    try:
        sess.commit()
        logging.log(logging.INFO, "Instance Done")
    except:
        sess.rollback()
        sentry.captureException()
        logging.log(logging.CRITICAL, 'Instance Error')
    finally:
        sess.remove()


@celeryapp.task
def crawl_spot_price(region, epoch):     # every minute triggered by ignite_crawler
    instance_list = sess.query(Instance).all()
    instance_type = [x.type for x in instance_list]

    end = datetime.datetime.strptime(epoch, '%Y-%m-%dT%H:%M:%S')
    start = end - datetime.timedelta(minutes=1)
    filters = [{"Name": "timestamp", "Values": [start.strftime('%Y-%m-%dT%H:%M:*')]}]

    client = boto3.client('ec2', region_name=region)
    price_history = client.describe_spot_price_history(StartTime=start, EndTime=end, Filters=filters)
    instance_set = set()
    for history_info in price_history['SpotPriceHistory']:
        if history_info['InstanceType'] not in instance_type:
            instance_set.add(history_info['InstanceType'])
    for instance in instance_set:
        sess.add(Instance(type=instance))
        sess.commit()
    for history_info in price_history['SpotPriceHistory']:
        sess.add(SpotPrice(az_name=history_info['AvailabilityZone'], product_desc=history_info['ProductDescription'],
                           instance_type=history_info['InstanceType'], price=float(history_info['SpotPrice']),
                           timestamp=history_info['Timestamp']))
    try:
        sess.commit()
        logging.log(logging.INFO, "Spot Price Done: {}".format(datetime.datetime.utcnow()))
    except:
        sess.rollback()
        sentry.captureException()
        logging.log(logging.CRITICAL, "Spot Price History Fail: {}".format(datetime.datetime.utcnow()))
    finally:
        sess.remove()


@celeryapp.task
def ignite_crawler():
    region_list = [x.name for x in sess.query(Region).all()]
    epoch = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    for region in region_list:
        crawl_spot_price.apply_async(args=[region, epoch], queue='crawl')
        print("{} Ignition".format(region))
