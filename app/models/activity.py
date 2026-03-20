from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(50))
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # CPM Fields
    duration = Column(Integer, default=1)
    early_start = Column(Integer, default=0)
    early_finish = Column(Integer, default=0)
    late_start = Column(Integer, default=0)
    late_finish = Column(Integer, default=0)
    total_float = Column(Integer, default=0)
    is_critical = Column(Boolean, default=False)
    
    # Resource Fields
    quantity = Column(Float, default=0.0)
    unit = Column(String(20))
    unit_cost = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Dates
    planned_start_date = Column(DateTime(timezone=True))
    planned_end_date = Column(DateTime(timezone=True))
    actual_start_date = Column(DateTime(timezone=True))
    actual_end_date = Column(DateTime(timezone=True))
    
    # Predecessors/Successors
    predecessors = Column(JSON, default=list)
    successors = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="activities")
    
    def __repr__(self):
        return f"<Activity {self.code}: {self.name}>"