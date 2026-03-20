from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from app.config.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.activity import Activity
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, BOQUploadResponse
from app.schemas.activity import ActivityCreate, ActivityResponse
from app.services.project_service import ProjectService
from app.services.cpm_service import CPMService
from app.utils.boq_parser import BOQParser

router = APIRouter(prefix="/projects", tags=["Projects"])

# Temporary function for development - NO AUTHENTICATION NEEDED
def get_test_user():
    """Return test user without authentication"""
    return User(id=1, email="test@example.com", username="testuser")

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Create a new construction project - No authentication required for development"""
    return ProjectService.create_project(db, project_data, current_user.id)

@router.get("/", response_model=List[ProjectResponse])
def get_user_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Get all projects - No authentication required for development"""
    return ProjectService.get_user_projects(db, current_user.id, skip, limit)

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Get project details"""
    return ProjectService.get_project(db, project_id, current_user.id)

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Update project details"""
    return ProjectService.update_project(db, project_id, current_user.id, project_data)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Delete project"""
    ProjectService.delete_project(db, project_id, current_user.id)

@router.post("/{project_id}/upload-boq", response_model=BOQUploadResponse)
async def upload_boq(
    project_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_test_user)  # No auth needed
):
    """Upload BOQ Excel file for a project"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )
    
    return await ProjectService.upload_boq(db, project_id, current_user.id, file)