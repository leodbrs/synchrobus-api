from typing import Union

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from sqlalchemy import select
from starlette.responses import RedirectResponse

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

app = FastAPI()


@app.get("/")
def root():
    response = RedirectResponse(url="/docs")
    return response


@app.get("/v1/bus")
def get_bus():
    """Return all bus"""
    session = APIDatabase(config.DB_URL)
    res = session.execute(select(Bus.id)).fetchall()
    session.close()
    return [bus[0] for bus in res]


@app.get("/v1/bus/direction")
def get_bus_direction(direction_id: Union[int, None] = None):
    """Return all bus for a direction"""
    if not direction_id:
        raise HTTPException(
            status_code=400, detail="Vous devez spécifier une direction"
        )
    query = select(Bus.id).where(
        Bus.id.in_(
            select(BusDirection.bus_id).where(BusDirection.direction_id == direction_id)
        )
    )
    session = APIDatabase(config.DB_URL)
    res = session.execute(query).fetchall()
    session.close()
    return [bus[0] for bus in res]


@app.get("/v1/direction")
def get_direction():
    """Return all direction"""
    session = APIDatabase(config.DB_URL)
    res = session.execute(select(Direction.id, Direction.name)).fetchall()
    session.close()
    return [{"id": direction[0], "name": direction[1]} for direction in res]


@app.get("/v1/direction/bus")
def get_direction_bus(bus_id: Union[str, None] = None):
    """Return all direction for a bus"""
    if not bus_id:
        raise HTTPException(status_code=400, detail="Vous devez spécifier un bus")
    query = select(Direction.id, Direction.name).where(
        Direction.id.in_(
            select(BusDirection.direction_id).where(BusDirection.bus_id == bus_id)
        )
    )
    session = APIDatabase(config.DB_URL)
    res = session.execute(query).fetchall()
    session.close()
    return [{"id": direction[0], "name": direction[1]} for direction in res]


@app.get("/v1/direction/bus_stop")
def get_direction_bus_stop(bus_stop_id: Union[str, None] = None):
    """Return all direction for a bus stop"""
    if not bus_stop_id:
        raise HTTPException(
            status_code=400, detail="Vous devez spécifier un arrêt de bus"
        )
    query = select(Direction.id, Direction.name).where(
        Direction.id.in_(
            select(BusStopDirection.direction_id).where(
                BusStopDirection.bus_stop_id == bus_stop_id
            )
        )
    )
    session = APIDatabase(config.DB_URL)
    res = session.execute(query).fetchall()
    session.close()
    return [{"id": direction[0], "name": direction[1]} for direction in res]


@app.get("/v1/appleshortcuts/direction/bus")
def get_direction_bus_appleshortcuts(bus_id: Union[str, None] = None):
    """Return all direction for a bus"""
    if not bus_id:
        raise HTTPException(status_code=400, detail="Vous devez spécifier un bus")
    query = select(Direction.id, Direction.name).where(
        Direction.id.in_(
            select(BusDirection.direction_id).where(BusDirection.bus_id == bus_id)
        )
    )
    session = APIDatabase(config.DB_URL)
    res = session.execute(query).fetchall()
    session.close()
    return {direction[1]: direction[0] for direction in res}


@app.get("/v1/bus_stop")
def get_bus_stop():
    """Return all bus stop"""
    session = APIDatabase(config.DB_URL)
    res = session.execute(select(BusStop.id, BusStop.name)).fetchall()
    session.close()
    return [{"id": bus_stop[0], "name": bus_stop[1]} for bus_stop in res]


@app.route("/v1/bus_stop/direction")
def get_bus_stop_direction(direction_id: Union[str, None] = None):
    """Return all bus stop for a direction"""
    if not direction_id:
        raise HTTPException(
            status_code=400, detail="Vous devez spécifier une direction"
        )
    query = select(BusStop.id, BusStop.name).where(
        BusStop.id.in_(
            select(BusStopDirection.bus_stop_id).where(
                BusStopDirection.direction_id == direction_id
            )
        )
    )
    session = APIDatabase(config.DB_URL)
    res = session.execute(query).fetchall()
    session.close()
    return [{"id": bus_stop[0], "name": bus_stop[1]} for bus_stop in res]


@app.get("/v1/appleshortcuts/bus_stop/direction")
def get_bus_stop_direction_appleshortcuts(direction_id: Union[str, None] = None):
    """Return all bus stop for a direction"""
    if not direction_id:
        raise HTTPException(
            status_code=400, detail="Vous devez spécifier une direction"
        )
    query = select(BusStop.id, BusStop.name).where(
        BusStop.id.in_(
            select(BusStopDirection.bus_stop_id).where(
                BusStopDirection.direction_id == direction_id
            )
        )
    )
    session = APIDatabase(config.DB_URL)
    res = session.execute(query).fetchall()
    session.close()
    return {bus_stop[1]: bus_stop[0] for bus_stop in res}


@app.get("/v1/bus_stop/search/{bus_stop_name}")
def search_bus_stop(bus_stop_name: str):
    """Return all bus stop that match the name"""
    query = select(BusStop.id, BusStop.name).where(
        BusStop.name.like(f"%{bus_stop_name}%")
    )
    session = APIDatabase(config.DB_URL)
    res = session.execute(query).fetchall()
    session.close()
    return [{"id": bus_stop[0], "name": bus_stop[1]} for bus_stop in res]


@app.get("/v1/bus_stop/live/{bus_stop_id}")
def get_bus_stop_info(bus_stop_id: str):
    if not bus_stop_id:
        raise HTTPException(
            status_code=400, detail="Vous devez spécifier un arrêt de bus"
        )
    headers = {'Accept-Encoding': 'gzip'}
    page = requests.get("https://live.synchro-bus.fr/" + bus_stop_id, headers=headers)

    soup = BeautifulSoup(page.content, "html.parser")
    bus_passage = soup.find_all("div", class_="nq-c-Direction")

    next_bus_list: list = []

    for div in bus_passage:
        next_bus = {
            # nom de la ligne
            "line": (div.find_all("img", class_="img-line")[0]["src"][56]),
            # direction de la ligne
            "direction": div.find_all(
                "div", class_="nq-c-Direction-content-detail-location"
            )[0].span.text,
            # heure d'arrivée
            "time": div.find_all("div", class_="nq-c-Direction-content-detail-time")[
                0
            ].text,
            # temps restant avant l'arrivée
            "remaining": div.find_all(
                "div", class_="nq-c-Direction-content-detail-remaining"
            )[0].text[1:]
            # The first character of the remaining str is a space
        }
        next_bus_list.append(next_bus)
    return next_bus_list
