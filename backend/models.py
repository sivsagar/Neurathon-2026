"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class TaskStartRequest(BaseModel):
    """Request to start a new task."""
    goal: str = Field(..., min_length=1, max_length=500, description="Natural language task description")


class MicroWinResponse(BaseModel):
    """Response containing a single micro-step."""
    task_id: str
    step_id: str
    step_text: str
    estimated_seconds: int
    simplification_level: int = 0
    step_order: int


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


class TaskResumeResponse(BaseModel):
    """Response when resuming a paused task."""
    task_id: str
    original_goal: str
    current_step: Optional[MicroWinResponse] = None
    status: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    details: Optional[str] = None
