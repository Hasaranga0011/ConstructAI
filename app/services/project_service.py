from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status, UploadFile
import os
import shutil
from datetime import datetime, timedelta
import json

from app.models.project import Project
from app.models.activity import Activity
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.schemas.activity import ActivityCreate
from app.utils.boq_parser import BOQParser
from app.services.cpm_service import CPMService

class ProjectService:
    
    @staticmethod
    def create_project(db: Session, project_data: ProjectCreate, user_id: int) -> Project:
        """Create a new project and save to database"""
        db_project = Project(
            name=project_data.name,
            description=project_data.description,
            location=project_data.location,
            start_date=project_data.start_date,
            end_date=project_data.end_date,
            created_by=user_id
        )
        
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        return db_project
    
    @staticmethod
    def get_project(db: Session, project_id: int, user_id: int) -> Project:
        """Get project by ID from database"""
        project = db.query(Project).filter(
            Project.id == project_id,
            Project.created_by == user_id
        ).first()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return project
    
    @staticmethod
    def get_user_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Project]:
        """Get all projects for a user from database"""
        return db.query(Project).filter(
            Project.created_by == user_id
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_project(db: Session, project_id: int, user_id: int, project_data: ProjectUpdate) -> Project:
        """Update project in database"""
        project = ProjectService.get_project(db, project_id, user_id)
        
        update_data = project_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(project, key, value)
        
        db.commit()
        db.refresh(project)
        
        return project
    
    @staticmethod
    def delete_project(db: Session, project_id: int, user_id: int):
        """Delete project from database"""
        project = ProjectService.get_project(db, project_id, user_id)
        
        # Delete BOQ file if exists
        if project.boq_file_path and os.path.exists(project.boq_file_path):
            os.remove(project.boq_file_path)
        
        db.delete(project)
        db.commit()
    
    @staticmethod
    async def upload_boq(
        db: Session, 
        project_id: int, 
        user_id: int, 
        file: UploadFile
    ) -> dict:
        """Upload and process BOQ file, save to database"""
        project = ProjectService.get_project(db, project_id, user_id)
        
        # Create upload directory
        upload_dir = "uploads/boq"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{upload_dir}/{project_id}_{timestamp}_{file.filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save file: {str(e)}"
            )
        
        # Parse BOQ
        try:
            activities_data = BOQParser.parse_boq(file_path)
        except Exception as e:
            # Clean up file if parsing fails
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse BOQ: {str(e)}"
            )
        
        # Delete existing activities from database
        db.query(Activity).filter(Activity.project_id == project_id).delete()
        
        # Create new activities in database
        total_cost = 0
        created_activities = []
        
        for act_data in activities_data:
            activity = Activity(
                project_id=project_id,
                code=act_data.get('code'),
                name=act_data.get('name'),
                description=act_data.get('description', ''),
                duration=act_data.get('duration', 1),
                quantity=act_data.get('quantity', 0),
                unit=act_data.get('unit', 'nos'),
                unit_cost=act_data.get('unit_cost', 0),
                total_cost=act_data.get('total_cost', 0),
                predecessors=act_data.get('predecessors', [])
            )
            db.add(activity)
            total_cost += act_data.get('total_cost', 0)
            created_activities.append(activity)
        
        # Update project in database
        project.boq_file_path = file_path
        project.total_cost = total_cost
        project.status = "active"  # Activate project after BOQ upload
        
        db.commit()
        
        return {
            "project_id": project_id,
            "activities_count": len(activities_data),
            "total_cost": total_cost,
            "message": "BOQ uploaded and saved to database successfully"
        }
    
    @staticmethod
    def generate_schedule(db: Session, project_id: int, user_id: int) -> dict:
        """Generate project schedule using CPM and save to database"""
        project = ProjectService.get_project(db, project_id, user_id)
        
        # Get activities from database
        activities = db.query(Activity).filter(Activity.project_id == project_id).all()
        
        if not activities:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No activities found. Please upload BOQ first."
            )
        
        # Build predecessor/successor relationships
        activity_map = {act.id: act for act in activities}
        
        # Clear existing successors
        for act in activities:
            act.successors = []
        
        # Build successor relationships
        for act in activities:
            if act.predecessors:
                for pred_id in act.predecessors:
                    if pred_id in activity_map:
                        if not activity_map[pred_id].successors:
                            activity_map[pred_id].successors = []
                        activity_map[pred_id].successors.append(act.id)
        
        # Validate network
        validation = CPMService.validate_network(activities)
        if not validation['valid']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid activity network: {', '.join(validation['errors'])}"
            )
        
        # Calculate CPM
        activities = CPMService.calculate_cpm(activities)
        
        # Calculate dates
        if project.start_date:
            activities = CPMService.calculate_dates(activities, project.start_date)
        
        # Get critical path
        critical_path = CPMService.get_critical_path(activities)
        
        # Generate Gantt data
        gantt_data = CPMService.generate_gantt_data(activities)
        
        # Update project duration
        if activities:
            max_finish = max([act.early_finish for act in activities])
            project.total_duration_days = max_finish
            
            if project.start_date:
                project.end_date = project.start_date + timedelta(days=max_finish)
        
        # Save schedule data to database
        project.schedule_data = {
            'gantt_data': gantt_data,
            'critical_path_ids': [act.id for act in critical_path],
            'total_duration': project.total_duration_days,
            'calculated_at': datetime.utcnow().isoformat(),
            'validation': validation
        }
        
        # Commit all changes to database
        db.commit()
        
        # Refresh to get updated data
        db.refresh(project)
        for act in activities:
            db.refresh(act)
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "total_duration": project.total_duration_days,
            "total_cost": project.total_cost,
            "critical_path": critical_path,
            "gantt_data": gantt_data,
            "activities": activities,
            "validation": validation,
            "message": "Schedule generated and saved to database"
        }