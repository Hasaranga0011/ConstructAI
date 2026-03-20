import pandas as pd
import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
import re

class BOQParser:
    """Parse BOQ Excel files and extract activities"""
    
    @staticmethod
    def parse_boq(file_path: str) -> List[Dict[str, Any]]:
        """
        Parse BOQ Excel file and extract activities
        
        Expected Excel format:
        - Code | Description | Quantity | Unit | Unit Cost | Duration | Predecessors
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # Normalize column names
            df.columns = [col.lower().strip() for col in df.columns]
            
            activities = []
            
            # Map expected columns
            code_col = BOQParser._find_column(df, ['code', 'activity code', 'id'])
            name_col = BOQParser._find_column(df, ['description', 'activity', 'name', 'work description'])
            qty_col = BOQParser._find_column(df, ['quantity', 'qty', 'qty.'], optional=True)
            unit_col = BOQParser._find_column(df, ['unit', 'uom'], optional=True)
            cost_col = BOQParser._find_column(df, ['unit cost', 'cost', 'rate'], optional=True)
            duration_col = BOQParser._find_column(df, ['duration', 'days', 'duration (days)'], optional=True)
            pred_col = BOQParser._find_column(df, ['predecessors', 'predecessor', 'depends on'], optional=True)
            
            for idx, row in df.iterrows():
                activity = {
                    'code': str(row[code_col]) if code_col and pd.notna(row[code_col]) else f"A{idx+1:03d}",
                    'name': str(row[name_col]) if name_col and pd.notna(row[name_col]) else f"Activity {idx+1}",
                    'description': str(row[name_col]) if name_col and pd.notna(row[name_col]) else "",
                    'quantity': float(row[qty_col]) if qty_col and pd.notna(row[qty_col]) else 1.0,
                    'unit': str(row[unit_col]) if unit_col and pd.notna(row[unit_col]) else "nos",
                    'unit_cost': float(row[cost_col]) if cost_col and pd.notna(row[cost_col]) else 0.0,
                    'duration': int(row[duration_col]) if duration_col and pd.notna(row[duration_col]) else 1,
                    'predecessors': BOQParser._parse_predecessors(str(row[pred_col])) if pred_col and pd.notna(row[pred_col]) else []
                }
                
                # Calculate total cost
                activity['total_cost'] = activity['quantity'] * activity['unit_cost']
                
                activities.append(activity)
            
            return activities
            
        except Exception as e:
            raise Exception(f"Failed to parse BOQ file: {str(e)}")
    
    @staticmethod
    def _find_column(df: pd.DataFrame, possible_names: List[str], optional: bool = False) -> str:
        """Find column by possible names"""
        for name in possible_names:
            if name in df.columns:
                return name
        if optional:
            return None
        raise Exception(f"Required column not found: {possible_names}")
    
    @staticmethod
    def _parse_predecessors(pred_str: str) -> List[int]:
        """Parse predecessor string to list of indices"""
        if not pred_str or pred_str.lower() in ['none', 'null', '']:
            return []
        
        # Parse formats like "1,2,3" or "1-2-3" or "1;2;3"
        pred_str = re.sub(r'[;,\-\s]+', ',', pred_str)
        preds = [int(p.strip()) for p in pred_str.split(',') if p.strip().isdigit()]
        return preds

    @staticmethod
    def create_sample_boq_template(file_path: str):
        """Create a sample BOQ template"""
        sample_data = {
            'Code': ['A001', 'A002', 'A003', 'A004', 'A005'],
            'Description': [
                'Site Clearing and Preparation',
                'Excavation and Earthwork',
                'Foundation Concrete',
                'Superstructure Concrete',
                'Finishing Works'
            ],
            'Quantity': [1000, 500, 100, 200, 300],
            'Unit': ['m²', 'm³', 'm³', 'm³', 'm²'],
            'Unit Cost': [5.00, 25.00, 80.00, 75.00, 15.00],
            'Duration (days)': [3, 5, 7, 10, 8],
            'Predecessors': ['', 'A001', 'A002', 'A003', 'A004']
        }
        
        df = pd.DataFrame(sample_data)
        df.to_excel(file_path, index=False, engine='openpyxl')