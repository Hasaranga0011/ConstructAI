from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    total_duration_days = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    status = Column(String(20), default="draft")
    boq_file_path = Column(String(500))
    schedule_data = Column(JSON)  # Store Gantt chart data
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    activities = relationship("Activity", back_populates="project", cascade="all, delete-orphan", lazy="dynamic")
    
    def __repr__(self):
        return f"<Project {self.name}>"