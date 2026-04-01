"""
Job Schema - Pydantic models for job posting data structure.
"""

from typing import List, Optional
from pydantic import BaseModel


class SalaryRange(BaseModel):
    """Salary range schema."""

    min_salary: float
    max_salary: float
    currency: str = "USD"


class JobRequirement(BaseModel):
    """Job requirement schema."""

    skill: str
    proficiency_level: Optional[str] = None
    years_required: Optional[int] = None
    is_required: bool = True


class JobPosting(BaseModel):
    """Job posting schema."""

    title: str
    company: str
    description: str
    location: str
    job_type: str  # Full-time, Part-time, Contract, etc.
    salary: Optional[SalaryRange] = None
    requirements: List[JobRequirement]
    nice_to_have: Optional[List[JobRequirement]] = None
    department: Optional[str] = None
    level: Optional[str] = None  # Junior, Mid, Senior, Executive
    posted_date: str
    deadline: Optional[str] = None
    remote_eligible: bool = False
