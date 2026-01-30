"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class TaskStartRequest(BaseModel):
    """Request to start a new task."""
    user_id: Optional[str] = None
    goal: str = Field(..., min_length=1, max_length=500, description="Natural language task description")
    energy_level: Optional[Literal["low", "medium", "high"]] = None


class MicroWinResponse(BaseModel):
    """Response containing a single micro-step."""
    task_id: str
    step_id: str
    step_text: str
    estimated_seconds: int
    simplification_level: int = 0
    step_order: int
    is_complete: bool = False
    next_preview: Optional[str] = None


class SimplifyRequest(BaseModel):
    """Request to simplify the current step."""
    task_id: str
    step_id: str
    reason: Optional[str] = None


class TaskActionRequest(BaseModel):
    """Request for task actions (done, pause)."""
    task_id: str
    step_id: str
    action: Literal["done", "pause"]
    duration_seconds: Optional[int] = None


class TaskResumeResponse(BaseModel):
    """Response when resuming a paused task."""
    task_id: str
    original_goal: str
    current_step: Optional[MicroWinResponse] = None
    status: str


class UserCreateRequest(BaseModel):
    """Request to create a new user profile."""
    name: str = Field(..., min_length=1, max_length=100)
    avatar_url: Optional[str] = None
    role: Literal["patient", "therapist"] = "patient"

class UserResponse(BaseModel):
    """User profile data with stats."""
    id: str
    name: str
    avatar_url: Optional[str]
    role: str
    xp: int
    level: int
    created_at: datetime

class DietTargetRequest(BaseModel):
    """Request to set a diet target."""
    user_id: str
    target_text: str

class DietTargetResponse(BaseModel):
    """Diet target data."""
    id: str
    user_id: str
    target_text: str
    completed: bool
    created_at: datetime

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    details: Optional[str] = None
