from typing import List, Dict, Any
from app.models.activity import Activity
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import numpy as np

class CPMService:
    """Critical Path Method Calculator"""
    
    @staticmethod
    def calculate_cpm(activities: List[Activity]) -> List[Activity]:
        """
        Calculate Critical Path Method for activities
        
        Returns activities with ES, EF, LS, LF, Float, and Critical flags
        """
        if not activities:
            return activities
        
        # Create activity map
        activity_map = {act.id: act for act in activities}
        adj_list = {act.id: [] for act in activities}
        
        # Build adjacency list
        for act in activities:
            if act.predecessors:
                for pred_id in act.predecessors:
                    if pred_id in activity_map:
                        adj_list[pred_id].append(act.id)
        
        # Forward Pass - Calculate ES and EF
        for act in activities:
            if not act.predecessors or len(act.predecessors) == 0:
                act.early_start = 0
                act.early_finish = act.duration
            else:
                max_ef = max([activity_map[pred_id].early_finish for pred_id in act.predecessors if pred_id in activity_map], default=0)
                act.early_start = max_ef
                act.early_finish = act.early_start + act.duration
        
        # Find project duration
        project_duration = max([act.early_finish for act in activities], default=0)
        
        # Backward Pass - Calculate LS and LF
        for act in reversed(activities):
            if not act.successors or len(act.successors) == 0:
                act.late_finish = project_duration
                act.late_start = act.late_finish - act.duration
            else:
                min_ls = min([activity_map[succ_id].late_start for succ_id in act.successors if succ_id in activity_map], default=project_duration)
                act.late_finish = min_ls
                act.late_start = act.late_finish - act.duration
        
        # Calculate Float and Critical Path
        for act in activities:
            act.total_float = act.late_start - act.early_start
            act.is_critical = act.total_float == 0
        
        return activities
    
    @staticmethod
    def get_critical_path(activities: List[Activity]) -> List[Activity]:
        """Get the critical path activities"""
        critical_activities = [act for act in activities if act.is_critical]
        
        # Sort by early start
        critical_activities.sort(key=lambda x: x.early_start)
        
        return critical_activities
    
    @staticmethod
    def calculate_dates(activities: List[Activity], project_start_date: datetime) -> List[Activity]:
        """Calculate planned dates based on CPM results"""
        if not activities or not project_start_date:
            return activities
        
        # Sort activities by early start
        sorted_activities = sorted(activities, key=lambda x: x.early_start)
        
        for act in sorted_activities:
            act.planned_start_date = project_start_date + timedelta(days=act.early_start)
            act.planned_end_date = project_start_date + timedelta(days=act.early_finish)
        
        return activities
    
    @staticmethod
    def generate_gantt_data(activities: List[Activity]) -> List[Dict[str, Any]]:
        """Generate Gantt chart data"""
        gantt_data = []
        
        for act in activities:
            gantt_data.append({
                'id': act.id,
                'name': act.name,
                'code': act.code,
                'start': act.planned_start_date.isoformat() if act.planned_start_date else None,
                'end': act.planned_end_date.isoformat() if act.planned_end_date else None,
                'duration': act.duration,
                'early_start': act.early_start,
                'early_finish': act.early_finish,
                'late_start': act.late_start,
                'late_finish': act.late_finish,
                'float': act.total_float,
                'critical': act.is_critical,
                'progress': 0,  # For future implementation
                'predecessors': act.predecessors
            })
        
        return gantt_data
    
    @staticmethod
    def validate_network(activities: List[Activity]) -> Dict[str, Any]:
        """Validate the network for cycles and logic errors"""
        errors = []
        warnings = []
        
        # Check for cycles
        if CPMService._has_cycle(activities):
            errors.append("Cycle detected in activity network")
        
        # Check for orphaned activities
        all_ids = {act.id for act in activities}
        referenced_ids = set()
        for act in activities:
            if act.predecessors:
                referenced_ids.update(act.predecessors)
        
        orphaned = all_ids - referenced_ids
        if len(orphaned) > 1:
            warnings.append(f"Multiple starting activities: {orphaned}")
        
        # Check for missing predecessors
        missing_preds = set()
        for act in activities:
            if act.predecessors:
                missing = set(act.predecessors) - all_ids
                if missing:
                    missing_preds.update(missing)
        
        if missing_preds:
            errors.append(f"Missing predecessor activities: {missing_preds}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    @staticmethod
    def _has_cycle(activities: List[Activity]) -> bool:
        """Detect cycles in activity network using DFS"""
        visited = set()
        rec_stack = set()
        adj = {act.id: act.predecessors or [] for act in activities}
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for act in activities:
            if act.id not in visited:
                if dfs(act.id):
                    return True
        
        return False