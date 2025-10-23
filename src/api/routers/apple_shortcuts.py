"""Apple Shortcuts specific routes (dict format instead of list)."""
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_db
from database.Table import Direction, BusDirection, BusStop, BusStopDirection
from core.logging_config import logger

router = APIRouter(prefix="/v1/appleshortcuts", tags=["apple_shortcuts"])


@router.get("/direction/bus", response_model=dict[str, int])
async def get_directions_by_bus_apple_shortcuts(
    bus_id: Union[str, None] = Query(None, description="Bus line identifier"),
    db: Session = Depends(get_db)
):
    """
    Get all directions for a bus in Apple Shortcuts format.
    
    Returns a dictionary with direction names as keys and IDs as values,
    which is compatible with Apple Shortcuts' dictionary/list choose action.
    
    Args:
        bus_id: The bus line identifier (e.g., "A", "B", "C")
        
    Returns:
        dict[str, int]: Dictionary mapping direction names to IDs
        
    Raises:
        HTTPException: 400 if bus_id is not provided
        
    Example response:
        {
            "Plage / technolac / landiers sud / gare": 1,
            "Université jacob": 2
        }
    """
    if not bus_id:
        raise HTTPException(
            status_code=400,
            detail="Vous devez spécifier un bus"
        )
    
    logger.info(f"GET /v1/appleshortcuts/direction/bus?bus_id={bus_id}")
    
    query = select(Direction.id, Direction.name).where(
        Direction.id.in_(
            select(BusDirection.direction_id).where(
                BusDirection.bus_id == bus_id
            )
        )
    )
    res = db.execute(query).fetchall()
    return {direction[1]: direction[0] for direction in res}


@router.get("/bus_stop/direction", response_model=dict[str, str])
async def get_bus_stops_by_direction_apple_shortcuts(
    direction_id: Union[str, None] = Query(None, description="Direction ID"),
    db: Session = Depends(get_db)
):
    """
    Get all bus stops for a direction in Apple Shortcuts format.
    
    Returns a dictionary with bus stop names as keys and IDs as values,
    which is compatible with Apple Shortcuts' dictionary/list choose action.
    
    Args:
        direction_id: The direction ID to filter by
        
    Returns:
        dict[str, str]: Dictionary mapping bus stop names to IDs
        
    Raises:
        HTTPException: 400 if direction_id is not provided
        
    Example response:
        {
            "Gambetta": "GAMBE1",
            "Gare": "GARE1",
            "Technolac": "INSEC1"
        }
    """
    if not direction_id:
        raise HTTPException(
            status_code=400,
            detail="Vous devez spécifier une direction"
        )
    
    logger.info(f"GET /v1/appleshortcuts/bus_stop/direction?direction_id={direction_id}")
    
    query = select(BusStop.id, BusStop.name).where(
        BusStop.id.in_(
            select(BusStopDirection.bus_stop_id).where(
                BusStopDirection.direction_id == direction_id
            )
        )
    )
    res = db.execute(query).fetchall()
    return {bus_stop[1]: bus_stop[0] for bus_stop in res}
