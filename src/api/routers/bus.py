"""Bus routes."""
from typing import Union
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.dependencies import get_db
from database.Table import Bus, BusDirection
from core.logging_config import logger

router = APIRouter(prefix="/v1/bus", tags=["bus"])


@router.get("/", response_model=list[str])
async def get_all_buses(db: Session = Depends(get_db)):
    """
    Get all available bus lines.
    
    Returns:
        list[str]: List of bus line identifiers (e.g., ["A", "B", "C", "D"])
    """
    logger.info("GET /v1/bus - Fetching all bus lines")
    res = db.execute(select(Bus.id)).fetchall()
    return [bus[0] for bus in res]


@router.get("/direction", response_model=list[str])
async def get_buses_by_direction(
    direction_id: Union[int, None] = Query(None, description="Direction ID"),
    db: Session = Depends(get_db)
):
    """
    Get all bus lines for a specific direction.
    
    Args:
        direction_id: The direction ID to filter by
        
    Returns:
        list[str]: List of bus line identifiers for the direction
        
    Raises:
        HTTPException: 400 if direction_id is not provided
    """
    if not direction_id:
        raise HTTPException(
            status_code=400,
            detail="Vous devez spécifier une direction"
        )
    
    logger.info(f"GET /v1/bus/direction?direction_id={direction_id}")
    
    query = select(Bus.id).where(
        Bus.id.in_(
            select(BusDirection.bus_id).where(
                BusDirection.direction_id == direction_id
            )
        )
    )
    res = db.execute(query).fetchall()
    return [bus[0] for bus in res]
