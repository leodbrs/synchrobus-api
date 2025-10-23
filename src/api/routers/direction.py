"""Direction routes."""
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_db
from database.Table import Direction, BusDirection, BusStopDirection
from models.schemas import DirectionResponse
from core.logging_config import logger

router = APIRouter(prefix="/v1/direction", tags=["direction"])


@router.get("/", response_model=list[DirectionResponse])
async def get_all_directions(db: Session = Depends(get_db)):
    """
    Get all available directions.
    
    Returns:
        list[DirectionResponse]: List of all directions with ID and name
    """
    logger.info("GET /v1/direction - Fetching all directions")
    res = db.execute(select(Direction.id, Direction.name)).fetchall()
    return [{"id": direction[0], "name": direction[1]} for direction in res]


@router.get("/bus", response_model=list[DirectionResponse])
async def get_directions_by_bus(
    bus_id: Union[str, None] = Query(None, description="Bus line identifier"),
    db: Session = Depends(get_db)
):
    """
    Get all directions for a specific bus line.
    
    Args:
        bus_id: The bus line identifier (e.g., "A", "B", "C")
        
    Returns:
        list[DirectionResponse]: List of directions for the bus
        
    Raises:
        HTTPException: 400 if bus_id is not provided
    """
    if not bus_id:
        raise HTTPException(
            status_code=400,
            detail="Vous devez spécifier un bus"
        )
    
    logger.info(f"GET /v1/direction/bus?bus_id={bus_id}")
    
    query = select(Direction.id, Direction.name).where(
        Direction.id.in_(
            select(BusDirection.direction_id).where(
                BusDirection.bus_id == bus_id
            )
        )
    )
    res = db.execute(query).fetchall()
    return [{"id": direction[0], "name": direction[1]} for direction in res]


@router.get("/bus_stop", response_model=list[DirectionResponse])
async def get_directions_by_bus_stop(
    bus_stop_id: Union[str, None] = Query(None, description="Bus stop identifier"),
    db: Session = Depends(get_db)
):
    """
    Get all directions for a specific bus stop.
    
    Args:
        bus_stop_id: The bus stop identifier (e.g., "GAMBE1")
        
    Returns:
        list[DirectionResponse]: List of directions serving this bus stop
        
    Raises:
        HTTPException: 400 if bus_stop_id is not provided
    """
    if not bus_stop_id:
        raise HTTPException(
            status_code=400,
            detail="Vous devez spécifier un arrêt de bus"
        )
    
    logger.info(f"GET /v1/direction/bus_stop?bus_stop_id={bus_stop_id}")
    
    query = select(Direction.id, Direction.name).where(
        Direction.id.in_(
            select(BusStopDirection.direction_id).where(
                BusStopDirection.bus_stop_id == bus_stop_id
            )
        )
    )
    res = db.execute(query).fetchall()
    return [{"id": direction[0], "name": direction[1]} for direction in res]
