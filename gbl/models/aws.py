from sqlalchemy import types, Column, ForeignKey
from sqlalchemy.orm import relationship

from gbl.models.base import Base


class Region(Base):
    __tablename__ = 'region'

    name = Column(types.Unicode(16), nullable=False)
    endpoint = Column(types.Unicode(32), nullable=False)


class AvailabilityZone(Base):
    __tablename__ = 'availability_zone'

    region_id = Column(types.Integer, ForeignKey('region.id'), nullable=False)
    region = relationship('Region', foreign_keys=[region_id])
    name = Column(types.Unicode(32), nullable=False)


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
