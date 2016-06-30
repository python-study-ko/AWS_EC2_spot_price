from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import types, Column, ForeignKey
from sqlalchemy.orm import relationship


class BaseClass(object):
    __table_args__ = {}

    id = Column(types.Integer, primary_key=True, nullable=False, autoincrement=True)

    def __repr__(self):
        if self.id:
            return "<class {} ID: {}>".format(type(self).__name__, self.id)
        else:
            return "<class {} ID: None>".format(type(self).__name__)


Base = declarative_base(cls=BaseClass)


class Region(Base):
    __tablename__ = 'region'

    name = Column(types.Unicode(16), nullable=False)
    endpoint = Column(types.Unicode(32), nullable=False)

    def __init__(self, region_name):
        self.name = region_name


class AvailabilityZone(Base):
    __tablename__ = 'availability_zone'

    region_id = Column(types.Integer, ForeignKey('region.id'), nullable=False)
    region = relationship('Region', foreign_keys=[region_id])
    name = Column(types.Unicode(32), nullable=False)

    def __init__(self, region_id, zone_name):
        self.region_id = region_id
        self.name = zone_name


class Product(Base):
    __tablename__ = 'product'

    description = Column(types.Unicode(16), nullable=False, index=True)


class Instance(Base):
    __tablename__ = 'instance'

    type = Column(types.Unicode(16), nullable=False)
    # TODO: add spec


class SpotPrice(Base):
    __tablename__ = 'spot_price'

    az_id = Column(types.Integer, ForeignKey('availability_zone.id'), nullable=False, index=True)
    az = relationship('AvailabilityZone', foreign_keys=[az_id])
    product_id = Column(types.Integer, ForeignKey('product.id'), nullable=False, index=True)
    product = relationship('Product', foreign_keys=[product_id])
    instance_id = Column(types.Integer, ForeignKey('instance.id'), nullable=False, index=True)
    instance = relationship('Instance', foreign_keys=[instance_id])
    timestamp = Column(types.DateTime, nullable=False)
    price = Column(types.Float, nullable=False)


class SearchLog(Base):
    __tablename__ = 'search_log'

    # TODO: scrap search log
