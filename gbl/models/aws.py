from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import types, Column, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class Region(Base):
    __tablename__ = 'region'

    name = Column(types.Unicode(16), primary_key=True, nullable=False, index=True)
    endpoint = Column(types.Unicode(32), nullable=False)

    def __init__(self, region_name):
        self.name = region_name


class AvailabilityZone(Base):
    __tablename__ = 'availability_zone'

    region_name = Column(types.Unicode(16), ForeignKey('region.name'), nullable=False)
    region = relationship('Region', foreign_keys=[region_name])
    name = Column(types.Unicode(32), primary_key=True, nullable=False, index=True)

    def __init__(self, region_name, zone_name):
        self.region_name = region_name
        self.name = zone_name


class Instance(Base):
    __tablename__ = 'instance'

    type = Column(types.Unicode(16), primary_key=True, nullable=False)
    # TODO: add spec


class SpotPrice(Base):
    __tablename__ = 'spot_price'

    id = Column(types.Integer, primary_key=True, autoincrement=True, nullable=False)
    az_name = Column(types.Unicode(32), ForeignKey('availability_zone.name'), nullable=False, index=True)
    az = relationship('AvailabilityZone', foreign_keys=[az_name])
    product = Column(types.Unicode(16), nullable=False, index=True)
    instance_type = Column(types.Unicode(16), ForeignKey('instance.type'), nullable=False, index=True)
    instance = relationship('Instance', foreign_keys=[instance_type])
    timestamp = Column(types.DateTime, nullable=False)
    price = Column(types.Float, nullable=False)

"""
class SearchLog(Base):
    __tablename__ = 'search_log'

    # TODO: scrap search log
"""
