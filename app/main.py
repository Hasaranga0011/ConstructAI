from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.routers import auth_router, project_router, schedule_router
from app.config.database import engine, Base
import uvicorn

# Create database tables automatically on startup
print("\n" + "="*50)
print("Starting ConstructAI Backend")
print("="*50)
print("Checking database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables ready")
print("="*50 + "\n")

# Create upload directories
os.makedirs("uploads/boq", exist_ok=True)

app = FastAPI(
    title="ConstructAI API",
    description="Backend API for ConstructAI - Project Planning & Scheduling System",
    version="2.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    swagger_ui_parameters={  # මේක එකතු කරන්න
        "persistAuthorization": True,  # Authorization remember කරන්න
        "tryItOutEnabled": True,  # Try it out default open කරන්න
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(schedule_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to ConstructAI API",
        "version": "2.0.0",
        "features": [
            "User Authentication",
            "Project Management",
            "BOQ Upload & Processing",
            "CPM Schedule Generation",
            "Gantt Chart Visualization"
        ],
        "documentation": "/swagger"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)