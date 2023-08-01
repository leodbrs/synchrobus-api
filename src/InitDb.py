import requests
from sqlalchemy import select

import config
from database.Database import APIDatabase as APIDatabase
from database.Table import (
    Bus,
    BusDirection,
    BusStop,
    BusStopBus,
    BusStopDirection,
    Direction,
)


def add_bus(bus):
    session.merge(Bus(id=bus))


def add_direction(direction):
    existing_row = session.execute(
        select(Direction).filter(Direction.name == direction.capitalize())
    ).first()
    if not existing_row:
        direction_item = Direction(name=direction.capitalize())
        session.add(direction_item)
        session.commit()
        return direction_item.id
    else:
        return existing_row[0].id


def add_bus_stop(bus_stop_id, bus_stop_name):
    existing_row = session.execute(
        select(BusStop).filter(BusStop.id == bus_stop_id)
    ).first()
    if not existing_row:
        bus_stop_item = BusStop(id=bus_stop_id, name=bus_stop_name)
        session.add(bus_stop_item)
        session.commit()
        return bus_stop_item.id
    else:
        return existing_row[0].id


def add_bus_direction(bus, direction):
    existing_row = session.execute(
        select(BusDirection).filter(
            BusDirection.bus_id == bus, BusDirection.direction_id == direction
        )
    ).first()
    if not existing_row:
        bus_direction_item = BusDirection(bus_id=bus, direction_id=direction)
        session.add(bus_direction_item)
        session.commit()
        return bus_direction_item.id
    else:
        return existing_row[0].id


def add_bus_stop_bus(bus_stop_id, bus):
    existing_row = session.execute(
        select(BusStopBus).filter(
            BusStopBus.bus_stop_id == bus_stop_id, BusStopBus.bus_id == bus
        )
    ).first()
    if not existing_row:
        bus_stop_bus_item = BusStopBus(bus_stop_id=bus_stop_id, bus_id=bus)
        session.add(bus_stop_bus_item)
        session.commit()
    else:
        return existing_row[0].id


def add_bus_stop_direction(bus_stop_id, direction):
    existing_row = session.execute(
        select(BusStopDirection).filter(
            BusStopDirection.bus_stop_id == bus_stop_id,
            BusStopDirection.direction_id == direction,
        )
    ).first()
    if not existing_row:
        bus_stop_direction_item = BusStopDirection(
            bus_stop_id=bus_stop_id, direction_id=direction
        )
        session.add(bus_stop_direction_item)
        session.commit()
    else:
        return existing_row[0].id


session = APIDatabase(config.DB_URL)

bus_list = ["A", "B", "C", "D", "1"]

for bus in bus_list:
    add_bus()
    synchrobus_api_info = requests.get(
        f"https://start.synchro.grandchambery.fr/fr/map/linesshape?line={bus}"
    ).json()[bus]

    for direction in synchrobus_api_info:
        direction_id = add_direction(direction["display"])
        add_bus_direction(bus, direction_id)

        for bus_stop in direction["stopPoints"]:
            add_bus_stop(bus_stop["id"], bus_stop["name"])
            add_bus_stop_bus(bus_stop["id"], bus)
            add_bus_stop_direction(bus_stop["id"], direction_id)
session.commit()
print("Database initialized")
