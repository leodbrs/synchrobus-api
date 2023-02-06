import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from sqlalchemy import select
from waitress import serve

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

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False


@app.route("/v1/bus", methods=["GET"])
def get_bus():
    """Return all bus"""
    res = session.execute(select(Bus.id)).fetchall()
    return jsonify([bus[0] for bus in res]), 200


@app.route("/v1/bus/direction", methods=["GET"])
def get_bus_direction():
    """Return all bus for a direction"""
    direction_id = request.args.get("id", default="", type=str)
    if direction_id == "":
        return jsonify({"error": "Vous devez spécifier une direction"}), 400
    query = select([Bus.id]).where(
        Bus.id.in_(
            select([BusDirection.bus_id]).where(
                BusDirection.direction_id == direction_id
            )
        )
    )
    res = session.execute(query).fetchall()
    return jsonify([bus[0] for bus in res]), 200


@app.route("/v1/direction", methods=["GET"])
def get_direction():
    """Return all direction"""
    res = session.execute(select(Direction.id, Direction.name)).fetchall()
    return (
        jsonify([{"id": direction[0], "name": direction[1]} for direction in res]),
        200,
    )


@app.route("/v1/direction/bus", methods=["GET"])
def get_direction_bus():
    """Return all direction for a bus"""
    bus_id = request.args.get("id", default="", type=str)
    if bus_id == "":
        return jsonify({"error": "Vous devez spécifier un bus"}), 400
    query = select([Direction.id, Direction.name]).where(
        Direction.id.in_(
            select([BusDirection.direction_id]).where(BusDirection.bus_id == bus_id)
        )
    )
    res = session.execute(query).fetchall()
    return (
        jsonify([{"id": direction[0], "name": direction[1]} for direction in res]),
        200,
    )


@app.route("/v1/direction/bus_stop", methods=["GET"])
def get_direction_bus_stop():
    """Return all direction for a bus stop"""
    bus_stop_id = request.args.get("id", default="", type=str)
    if bus_stop_id == "":
        return jsonify({"error": "Vous devez spécifier un arrêt de bus"}), 400
    query = select([Direction.id, Direction.name]).where(
        Direction.id.in_(
            select([BusStopDirection.direction_id]).where(
                BusStopDirection.bus_stop_id == bus_stop_id
            )
        )
    )
    res = session.execute(query).fetchall()
    return (
        jsonify([{"id": direction[0], "name": direction[1]} for direction in res]),
        200,
    )


@app.route("/v1/appleshortcuts/direction/bus", methods=["GET"])
def get_direction_bus_appleshortcuts():
    """Return all direction for a bus"""
    bus_id = request.args.get("id", default="", type=str)
    if bus_id == "":
        return jsonify({"error": "Vous devez spécifier un bus"}), 400
    query = select([Direction.id, Direction.name]).where(
        Direction.id.in_(
            select([BusDirection.direction_id]).where(BusDirection.bus_id == bus_id)
        )
    )
    res = session.execute(query).fetchall()
    return (
        jsonify({direction[1]: direction[0] for direction in res}),
        200,
    )


@app.route("/v1/bus_stop", methods=["GET"])
def get_bus_stop():
    """Return all bus stop"""
    res = session.execute(select(BusStop.id, BusStop.name)).fetchall()
    return (
        jsonify([{"id": bus_stop[0], "name": bus_stop[1]} for bus_stop in res]),
        200,
    )


@app.route("/v1/bus_stop/direction", methods=["GET"])
def get_bus_stop_direction():
    """Return all bus stop for a direction"""
    direction_id = request.args.get("id", default="", type=str)
    if direction_id == "":
        return jsonify({"error": "Vous devez spécifier une direction"}), 400
    query = select([BusStop.id, BusStop.name]).where(
        BusStop.id.in_(
            select([BusStopDirection.bus_stop_id]).where(
                BusStopDirection.direction_id == direction_id
            )
        )
    )
    res = session.execute(query).fetchall()
    return (
        jsonify([{"id": bus_stop[0], "name": bus_stop[1]} for bus_stop in res]),
        200,
    )


@app.route("/v1/appleshortcuts/bus_stop/direction", methods=["GET"])
def get_bus_stop_direction_appleshortcuts():
    """Return all bus stop for a direction"""
    direction_id = request.args.get("id", default="", type=str)
    if direction_id == "":
        return jsonify({"error": "Vous devez spécifier une direction"}), 400
    query = select([BusStop.id, BusStop.name]).where(
        BusStop.id.in_(
            select([BusStopDirection.bus_stop_id]).where(
                BusStopDirection.direction_id == direction_id
            )
        )
    )
    res = session.execute(query).fetchall()
    return (
        jsonify({bus_stop[1]: bus_stop[0] for bus_stop in res}),
        200,
    )


@app.route("/v1/bus_stop/search/<string:bus_stop_name>", methods=["GET"])
def search_bus_stop(bus_stop_name: str):
    """Return all bus stop that match the name"""
    query = select([BusStop.id, BusStop.name]).where(
        BusStop.name.like(f"%{bus_stop_name}%")
    )
    res = session.execute(query).fetchall()
    return (
        jsonify([{"id": bus_stop[0], "name": bus_stop[1]} for bus_stop in res]),
        200,
    )


@app.route("/v1/bus_stop/live/<string:bus_stop_id>", methods=["GET"])
def get_bus_stop_info(bus_stop_id: str):
    if bus_stop_id == "":
        return jsonify({"error": "Vous devez spécifier un arrêt de bus"}), 400
    page = requests.get("https://live.synchro-bus.fr/" + bus_stop_id)

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
    return jsonify(next_bus_list)


if __name__ == "__main__":
    session = APIDatabase(config.DB_URL)
    print("Starting server...")
    app.run(host="0.0.0.0", port=8080, debug=True)
    # serve(app, host="0.0.0.0", port=8080)
