"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# ============================================================================
# Base Schemas
# ============================================================================

class BusResponse(BaseModel):
    """Schema for bus response."""
    id: str = Field(..., description="Bus line identifier (e.g., A, B, C, D)")


class DirectionBase(BaseModel):
    """Base schema for direction."""
    id: int = Field(..., description="Direction ID")
    name: str = Field(..., description="Direction name")
    
    model_config = ConfigDict(from_attributes=True)


class DirectionResponse(DirectionBase):
    """Schema for direction response."""
    pass


class BusStopBase(BaseModel):
    """Base schema for bus stop."""
    id: str = Field(..., description="Bus stop identifier (e.g., GAMBE1)")
    name: str = Field(..., description="Bus stop name")
    
    model_config = ConfigDict(from_attributes=True)


class BusStopResponse(BusStopBase):
    """Schema for bus stop response."""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "GAMBE1",
                "name": "Gambetta"
            }
        }
    )


# ============================================================================
# Apple Shortcuts Schemas (dict format)
# ============================================================================
# Note: These are not used in response_model as FastAPI handles dict directly


# ============================================================================
# Live Bus Info Schemas
# ============================================================================

class BusLiveInfoResponse(BaseModel):
    """Schema for live bus information at a stop."""
    line: str = Field(..., description="Bus line (e.g., A, B, C)")
    direction: str = Field(..., description="Destination direction")
    time: str = Field(..., description="Arrival time (HH:MM)")
    remaining: str = Field(..., description="Time remaining (e.g., 'dans 5 minutes')")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "line": "A",
                "direction": "Université Jacob",
                "time": "20:26",
                "remaining": "dans 2 minutes"
            }
        }
    )


# ============================================================================
# Query Parameters Schemas
# ============================================================================

class BusQueryParams(BaseModel):
    """Query parameters for bus-related endpoints."""
    bus_id: Optional[str] = Field(None, description="Bus line identifier")


class DirectionQueryParams(BaseModel):
    """Query parameters for direction-related endpoints."""
    direction_id: Optional[int] = Field(None, description="Direction ID")


class BusStopQueryParams(BaseModel):
    """Query parameters for bus stop endpoints."""
    bus_stop_id: Optional[str] = Field(None, description="Bus stop identifier")
