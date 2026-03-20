from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any  # මේ import එකත් එකතු කරන්න
from enum import Enum

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    status: Optional[ProjectStatus] = None
    total_duration_days: Optional[int] = None
    total_cost: Optional[float] = None

class ProjectResponse(ProjectBase):
    id: int
    total_duration_days: Optional[int] = None
    total_cost: Optional[float] = None
    status: ProjectStatus
    boq_file_path: Optional[str] = None
    schedule_data: Optional[Dict[str, Any]] = None  # Dict එක හරියට වැඩ කරයි
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BOQUploadResponse(BaseModel):
    project_id: int
    activities_count: int
    total_cost: float
    message: str