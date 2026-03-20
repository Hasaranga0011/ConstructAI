from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any  # Dict සහ Any import කරන්න ඕන

class ActivityBase(BaseModel):
    code: Optional[str] = None
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    duration: int = Field(1, ge=1, le=365)
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_cost: Optional[float] = Field(None, ge=0)
    predecessors: List[int] = []

class ActivityCreate(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = Field(None, ge=1, le=365)
    quantity: Optional[float] = None
    unit_cost: Optional[float] = Field(None, ge=0)
    predecessors: Optional[List[int]] = None

class ActivityResponse(ActivityBase):
    id: int
    project_id: int
    total_cost: Optional[float] = None
    
    # CPM Results
    early_start: int
    early_finish: int
    late_start: int
    late_finish: int
    total_float: int
    is_critical: bool
    
    # Dates
    planned_start_date: Optional[datetime] = None
    planned_end_date: Optional[datetime] = None
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ScheduleResponse(BaseModel):
    project_id: int
    project_name: str
    total_duration: int
    total_cost: float
    critical_path: List[ActivityResponse]
    gantt_data: List[Dict[str, Any]]  # දැන් Dict හරියට වැඩ කරයි
    activities: List[ActivityResponse]