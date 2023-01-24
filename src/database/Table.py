from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Bus(Base):
    __tablename__ = "bus"

    id = Column("id", String(255), primary_key=True)

    def __init__(self, id):
        self.id = id


class Direction(Base):
    __tablename__ = "direction"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(255), unique=True)

    def __init__(self, name):
        self.name = name


class BusStop(Base):
    __tablename__ = "bus_stop"

    id = Column("id", String(255), primary_key=True)
    name = Column("name", String(255))

    def __init__(self, id, name):
        self.id = id
        self.name = name


class BusDirection(Base):
    __tablename__ = "bus_direction"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    bus_id = Column("bus_id", String(255), ForeignKey("bus.id"))
    direction_id = Column("direction_id", Integer, ForeignKey("direction.id"))

    def __init__(self, bus_id, direction_id):
        self.bus_id = bus_id
        self.direction_id = direction_id


class BusStopBus(Base):
    __tablename__ = "bus_stop_bus"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    bus_id = Column("bus_id", String(255), ForeignKey("bus.id"))
    bus_stop_id = Column("bus_stop_id", String(255), ForeignKey("bus_stop.id"))

    def __init__(self, bus_id, bus_stop_id):
        self.bus_id = bus_id
        self.bus_stop_id = bus_stop_id


class BusStopDirection(Base):
    __tablename__ = "bus_stop_direction"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    bus_stop_id = Column("bus_stop_id", String(255), ForeignKey("bus_stop.id"))
    direction_id = Column("direction_id", Integer, ForeignKey("direction.id"))

    def __init__(self, bus_stop_id, direction_id):
        self.bus_stop_id = bus_stop_id
        self.direction_id = direction_id
