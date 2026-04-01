"""
Application Schema - Pydantic models for job application data structure.
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class JobApplication(BaseModel):
    """Job application schema."""

    candidate_id: str
    job_id: str
    resume_id: str
    cover_letter: Optional[str] = None
    custom_questions: Optional[dict] = None
    applied_date: datetime
    status: str  # Applied, Reviewed, Shortlisted, Rejected, Offered, Hired
    match_score: Optional[float] = None
    notes: Optional[str] = None


class ApplicationStatus(BaseModel):
    """Application status tracking schema."""

    application_id: str
    current_status: str
    status_history: list
    updated_date: datetime
    next_step: Optional[str] = None
    feedback: Optional[str] = None
