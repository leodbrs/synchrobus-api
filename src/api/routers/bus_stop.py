"""Bus stop routes."""
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy import select
from sqlalchemy.orm import Session
import requests
from bs4 import BeautifulSoup

from api.dependencies import get_db
from database.Table import BusStop, BusStopDirection
from models.schemas import BusStopResponse, BusLiveInfoResponse
from core.logging_config import logger

router = APIRouter(prefix="/v1/bus_stop", tags=["bus_stop"])


@router.get("/", response_model=list[BusStopResponse])
async def get_all_bus_stops(db: Session = Depends(get_db)):
    """
    Get all available bus stops.
    
    Returns:
        list[BusStopResponse]: List of all bus stops with ID and name
    """
    logger.info("GET /v1/bus_stop - Fetching all bus stops")
    res = db.execute(select(BusStop.id, BusStop.name)).fetchall()
    return [{"id": bus_stop[0], "name": bus_stop[1]} for bus_stop in res]


@router.get("/direction", response_model=list[BusStopResponse])
async def get_bus_stops_by_direction(
    direction_id: Union[str, None] = Query(None, description="Direction ID"),
    db: Session = Depends(get_db)
):
    """
    Get all bus stops for a specific direction.
    
    Args:
        direction_id: The direction ID to filter by
        
    Returns:
        list[BusStopResponse]: List of bus stops for the direction
        
    Raises:
        HTTPException: 400 if direction_id is not provided
    """
    if not direction_id:
        raise HTTPException(
            status_code=400,
            detail="Vous devez spécifier une direction"
        )
    
    logger.info(f"GET /v1/bus_stop/direction?direction_id={direction_id}")
    
    query = select(BusStop.id, BusStop.name).where(
        BusStop.id.in_(
            select(BusStopDirection.bus_stop_id).where(
                BusStopDirection.direction_id == direction_id
            )
        )
    )
    res = db.execute(query).fetchall()
    return [{"id": bus_stop[0], "name": bus_stop[1]} for bus_stop in res]


@router.get("/search/{bus_stop_name}", response_model=list[BusStopResponse])
async def search_bus_stops(
    bus_stop_name: str = Path(..., description="Bus stop name to search for"),
    db: Session = Depends(get_db)
):
    """
    Search for bus stops by name.
    
    Args:
        bus_stop_name: The name pattern to search for
        
    Returns:
        list[BusStopResponse]: List of bus stops matching the search query
    """
    logger.info(f"GET /v1/bus_stop/search/{bus_stop_name}")
    
    query = select(BusStop.id, BusStop.name).where(
        BusStop.name.like(f"%{bus_stop_name}%")
    )
    res = db.execute(query).fetchall()
    return [{"id": bus_stop[0], "name": bus_stop[1]} for bus_stop in res]


@router.get("/live/{bus_stop_id}", response_model=list[BusLiveInfoResponse])
async def get_bus_stop_live_info(
    bus_stop_id: str = Path(..., description="Bus stop identifier")
):
    """
    Get real-time bus arrival information for a specific stop.
    
    This endpoint scrapes live data from the Synchro-Bus website.
    
    Args:
        bus_stop_id: The bus stop identifier (e.g., "GAMBE1")
        
    Returns:
        list[BusLiveInfoResponse]: List of upcoming bus arrivals with times
        
    Raises:
        HTTPException: 400 if bus_stop_id is not provided
        HTTPException: 500 if scraping fails
    """
    if not bus_stop_id:
        raise HTTPException(
            status_code=400,
            detail="Vous devez spécifier un arrêt de bus"
        )
    
    logger.info(f"GET /v1/bus_stop/live/{bus_stop_id} - Fetching live data")
    
    try:
        headers = {'Accept-Encoding': 'gzip'}
        page = requests.get(
            f"https://live.synchro-bus.fr/{bus_stop_id}",
            headers=headers,
            timeout=10
        )
        page.raise_for_status()
        
        soup = BeautifulSoup(page.content, "html.parser")
        bus_passage = soup.find_all("div", class_="nq-c-Direction")
        
        next_bus_list: list = []
        
        for div in bus_passage:
            try:
                next_bus = {
                    # Bus line identifier
                    "line": div.find_all("img", class_="img-line")[0]["src"][56],
                    # Direction name
                    "direction": div.find_all(
                        "div", class_="nq-c-Direction-content-detail-location"
                    )[0].span.text,
                    # Arrival time
                    "time": div.find_all(
                        "div", class_="nq-c-Direction-content-detail-time"
                    )[0].text,
                    # Time remaining
                    "remaining": div.find_all(
                        "div", class_="nq-c-Direction-content-detail-remaining"
                    )[0].text[1:]  # Remove first space character
                }
                next_bus_list.append(next_bus)
            except (IndexError, KeyError, AttributeError) as e:
                logger.warning(f"Error parsing bus passage data: {e}")
                continue
        
        return next_bus_list
        
    except requests.RequestException as e:
        logger.error(f"Error fetching live data for {bus_stop_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la récupération des données en temps réel: {str(e)}"
        )
