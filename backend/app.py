"""FastAPI application - MicroWin API."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging

from database import db
from models import (
    TaskStartRequest,
    MicroWinResponse,
    SimplifyRequest,
    TaskActionRequest,
    TaskResumeResponse,
    ErrorResponse
)
from services.microwin_service import microwin_service
from services.scheduler_service import scheduler_service

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: Initialize database
    await db.init_db()
    logger.info("Database initialized")
    yield
    # Shutdown: Cleanup if needed
    logger.info("Application shutdown")


# Initialize FastAPI app
app = FastAPI(
    title="MicroWin: The Cognitive Prosthetic API",
    description="Cognitive prosthetic for neurodivergent users - Task Initiation support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For hackathon - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/task/start", response_model=MicroWinResponse)
async def start_task(request: TaskStartRequest):
    """
    Start a new task and get the first micro-step.
    
    This endpoint:
    1. Creates a new task in the database
    2. Generates the first micro-win using AI
    3. Returns the step to display
    """
    try:
        # Create task in database with optional energy level
        task_id = await db.create_task(request.goal, energy_level=request.energy_level)
        logger.info(f"Created task {task_id} (Energy: {request.energy_level}) for goal: {request.goal}")
        
        # Generate first micro-step
        step_data = await microwin_service.generate_initial_step(
            request.goal, 
            energy_level=request.energy_level or "medium"
        )
        
        # Save step to database
        step_order = 0
        step_id = await db.create_step(
            task_id=task_id,
            step_text=step_data["step"],
            estimated_seconds=step_data["estimated_seconds"],
            step_order=step_order,
            simplification_level=0
        )
        
        logger.info(f"Generated first step for task {task_id}: {step_data['step']}")
        
        return MicroWinResponse(
            task_id=task_id,
            step_id=step_id,
            step_text=step_data["step"],
            estimated_seconds=step_data["estimated_seconds"],
            simplification_level=0,
            step_order=step_order,
            is_complete=step_data.get("is_complete", False)
        )
    
    except Exception as e:
        logger.error(f"Error starting task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/task/next", response_model=MicroWinResponse)
async def next_step(request: TaskActionRequest):
    """
    Mark current step as done and get next micro-step.
    
    This endpoint:
    1. Marks the current step as completed
    2. Generates the next micro-win
    3. Returns the new step
    """
    try:
        # Mark current step as completed with duration
        await db.mark_step_completed(request.step_id, duration=request.duration_seconds)
        logger.info(f"Completed step {request.step_id} in {request.duration_seconds}s")
        
        # Get task details
        task = await db.get_task(request.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Get the completed step text for context
        completed_step = await db.get_step(request.step_id)
        previous_step_text = completed_step["step_text"] if completed_step else ""
        
        # Generate next step
        step_data = await microwin_service.generate_next_step(
            goal=task["original_goal"],
            previous_step=previous_step_text,
            energy_level=task.get("energy_level") or "medium"
        )
        
        # Save new step
        next_order = await db.get_next_step_order(request.task_id)
        step_id = await db.create_step(
            task_id=request.task_id,
            step_text=step_data["step"],
            estimated_seconds=step_data["estimated_seconds"],
            step_order=next_order,
            simplification_level=0
        )
        
        logger.info(f"Generated next step for task {request.task_id}: {step_data['step']}")
        
        return MicroWinResponse(
            task_id=request.task_id,
            step_id=step_id,
            step_text=step_data["step"],
            estimated_seconds=step_data["estimated_seconds"],
            simplification_level=0,
            step_order=next_order,
            is_complete=step_data.get("is_complete", False)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/task/simplify", response_model=MicroWinResponse)
async def simplify_step(request: SimplifyRequest):
    """
    Simplify current step (user clicked 'Too Hard').
    
    This endpoint:
    1. Gets the current step
    2. Generates a simpler version
    3. Replaces the current step
    """
    try:
        # Get current step
        current_step = await db.get_current_step(request.task_id)
        if not current_step:
            raise HTTPException(status_code=404, detail="No current step found")
        
        # Generate simplified step
        step_data = await microwin_service.simplify_step(
            current_step=current_step["step_text"],
            simplification_level=current_step["simplification_level"]
        )
        
        # Create new simplified step (keep same order, increment simplification level)
        new_step_id = await db.create_step(
            task_id=request.task_id,
            step_text=step_data["step"],
            estimated_seconds=step_data["estimated_seconds"],
            step_order=current_step["step_order"],
            simplification_level=current_step["simplification_level"] + 1
        )
        
        # Mark old step as completed (effectively replacing it)
        await db.mark_step_completed(current_step["id"])
        
        logger.info(f"Simplified step for task {request.task_id}: {step_data['step']}")
        
        return MicroWinResponse(
            task_id=request.task_id,
            step_id=new_step_id,
            step_text=step_data["step"],
            estimated_seconds=step_data["estimated_seconds"],
            simplification_level=current_step["simplification_level"] + 1,
            step_order=current_step["step_order"],
            is_complete=step_data.get("is_complete", False)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error simplifying step: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/task/pause")
async def pause_task(request: TaskActionRequest):
    """
    Pause current task (save state for later).
    """
    try:
        await db.update_task_status(request.task_id, "paused")
        logger.info(f"Paused task {request.task_id}")
        return {"status": "paused", "task_id": request.task_id}
    
    except Exception as e:
        logger.error(f"Error pausing task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/task/resume/{task_id}", response_model=TaskResumeResponse)
async def resume_task(task_id: str):
    """
    Resume a paused task.
    """
    try:
        task = await db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        current_step = await db.get_current_step(task_id)
        
        # Update status to active
        await db.update_task_status(task_id, "active")
        
        step_response = None
        if current_step:
            step_response = MicroWinResponse(
                task_id=task_id,
                step_id=current_step["id"],
                step_text=current_step["step_text"],
                estimated_seconds=current_step["estimated_seconds"],
                simplification_level=current_step["simplification_level"],
                step_order=current_step["step_order"]
            )
        
        return TaskResumeResponse(
            task_id=task_id,
            original_goal=task["original_goal"],
            current_step=step_response,
            status="active"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/insights")
async def get_insights():
    """
    Get energy-adaptive scheduler insights.
    Analyzes historical data to find peak cognitive hours.
    """
    try:
        return await scheduler_service.get_energy_insights()
    except Exception as e:
        logger.error(f"Error getting insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "MicroWin"}


# Mount static files (frontend)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
