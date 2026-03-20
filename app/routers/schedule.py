from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.config.database import get_db
from app.models.user import User
from app.schemas.activity import ActivityResponse, ActivityCreate, ActivityUpdate, ScheduleResponse
from app.services.project_service import ProjectService
from app.services.cpm_service import CPMService
from app.models.activity import Activity

router = APIRouter(prefix="/schedule", tags=["Schedule"])

# Temporary function for development - NO AUTHENTICATION NEEDED
def get_test_user():
    """Return test user without authentication"""
    return User(id=1, email="test@example.com", username="testuser")

@router.post("/{project_id}/generate", response_model=ScheduleResponse)
def generate_schedule(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Generate project schedule using CPM - No authentication required"""
    result = ProjectService.generate_schedule(db, project_id, current_user.id)
    return result

@router.get("/{project_id}", response_model=ScheduleResponse)
def get_schedule(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Get generated schedule for a project"""
    project = ProjectService.get_project(db, project_id, current_user.id)
    
    if not project.schedule_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not generated yet. Please generate schedule first."
        )
    
    activities = db.query(Activity).filter(Activity.project_id == project_id).all()
    
    return {
        "project_id": project.id,
        "project_name": project.name,
        "total_duration": project.total_duration_days,
        "total_cost": project.total_cost,
        "critical_path": [act for act in activities if act.is_critical],
        "gantt_data": project.schedule_data.get('gantt_data', []),
        "activities": activities
    }

@router.get("/{project_id}/critical-path", response_model=List[ActivityResponse])
def get_critical_path(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Get critical path activities"""
    project = ProjectService.get_project(db, project_id, current_user.id)
    
    activities = db.query(Activity).filter(
        Activity.project_id == project_id,
        Activity.is_critical == True
    ).order_by(Activity.early_start).all()
    
    return activities

@router.post("/{project_id}/activities", response_model=ActivityResponse)
def create_activity(
    project_id: int,
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Create a new activity for a project"""
    # Check project exists
    project = ProjectService.get_project(db, project_id, current_user.id)
    
    activity = Activity(
        project_id=project_id,
        **activity_data.dict()
    )
    
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    return activity

@router.put("/activities/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Update an activity"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Verify project ownership
    project = ProjectService.get_project(db, activity.project_id, current_user.id)
    
    for key, value in activity_data.dict(exclude_unset=True).items():
        setattr(activity, key, value)
    
    db.commit()
    db.refresh(activity)
    
    return activity

@router.delete("/activities/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Delete an activity"""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    
    # Verify project ownership
    project = ProjectService.get_project(db, activity.project_id, current_user.id)
    
    db.delete(activity)
    db.commit()