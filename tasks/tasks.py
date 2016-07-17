import datetime
import logging
import json

import boto3
import requests
from bs4 import BeautifulSoup
import re

from tasks.celery_settings import DEFAULT_REGION
from tasks.celeryapp import celeryapp
from gbl.models.aws import Region, AvailabilityZone, Instance, SpotPrice, OndemandPrice
from gbl.common import sess, sentry, URL_DICT


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
    except Exception as e:
        sess.rollback()
        sentry.captureException()
        logging.log(logging.CRITICAL, 'Instance Error: {}'.format(e))
    finally:
        sess.remove()


@celeryapp.task
def crawl_on_demand():  # once a day
    region_list = [x.name for x in sess.query(Region).all()]
    instance_dict = dict(sess.query(Instance.type, Instance).all())
    od_price_list = sess.query(OndemandPrice).all()
    od_price_dict = dict([((x.region_name, x.instance_type, x.product), x) for x in od_price_list])

    for url in URL_DICT.values():
        res = requests.get(url)
        regions = get_info(res.text)
        for region in regions:
            region_name = region['region']
            if region_name not in region_list:
                continue
            for instance_info in region['instanceTypes']:
                for instance_types in instance_info['sizes']:
                    instance_type = instance_types['size']
                    product_desc = instance_types['valueColumns'][0]['name']
                    try:
                        price = float(instance_types['valueColumns'][0]['prices']['USD'])
                    except ValueError:
                        price = None
                    if instance_type not in instance_dict.keys():
                        continue
                    instance = instance_dict[instance_type]
                    instance.set_spec(**instance_types)
                    if (region_name, instance_type, product_desc) in od_price_dict:
                        od_price = od_price_dict[(region_name, instance_type, product_desc)]
                    else:
                        od_price = OndemandPrice(region_name, instance_type, product_desc)
                    od_price.set_price(price)
                    sess.add_all([instance, od_price])
    try:
        sess.commit()
        logging.log(logging.INFO, "Instance Spec, OD_Price Done")
    except Exception as e:
        sess.rollback()
        sentry.captureException()
        logging.log(logging.CRITICAL, "Instance Spec, OD_Price Fail: {}".format(e))


def get_info(txt):
    orig = txt.split('\n')[-1][9:-2]
    orig2 = orig.replace('{', '{"')
    orig3 = orig2.replace(',', ',"')
    orig4 = orig3.replace(',"{', ',{')
    orig5 = orig4.replace(':', '":')
    orig6 = orig5.replace(',""', ',"')
    j = json.loads(orig6)
    return j['config']['regions']


@celeryapp.task
def crawl_spot_price(region, epoch):     # every minute triggered by ignite_crawler
    end = datetime.datetime.strptime(epoch, '%Y-%m-%dT%H:%M:%S')
    start = end - datetime.timedelta(minutes=1)
    filters = [{"Name": "timestamp", "Values": [start.strftime('%Y-%m-%dT%H:%M:*')]}]
    get_instance = False

    client = boto3.client('ec2', region_name=region)
    next_token = ""
    while True:
        price_history = client.describe_spot_price_history(StartTime=start, EndTime=end, Filters=filters,
                                                           MaxResults=100, NextToken=next_token)
        next_token = price_history.get('NextToken', "")
        logging.log(logging.INFO, "{} length: {}, token: {}".format(region, len(price_history['SpotPriceHistory']), next_token))
        instance_list = [x.type for x in sess.query(Instance).all()]

        for history_info in price_history['SpotPriceHistory']:
            new_price = SpotPrice(az_name=history_info['AvailabilityZone'], product_desc=history_info['ProductDescription'],
                                  instance_type=history_info['InstanceType'], price=float(history_info['SpotPrice']),
                                  timestamp=history_info['Timestamp'])
            if new_price.instance_type not in instance_list:
                get_instance = True
            sess.add(new_price)
        if next_token:
            continue
        else:
            break

    if get_instance:
        crawl_instance_type()
        sess.add_all()

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
        logging.log(logging.INFO, "{} Ignition".format(region))
