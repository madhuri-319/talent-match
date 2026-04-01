"""
Resume Schema - Pydantic models for resume data structure.
"""

from typing import List, Optional
from pydantic import BaseModel, EmailStr, HttpUrl


class ContactInfo(BaseModel):
    """Contact information schema."""

    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[HttpUrl] = None


class WorkExperience(BaseModel):
    """Work experience schema."""

    title: str
    company: str
    start_date: str
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None
    achievements: Optional[List[str]] = None


class Education(BaseModel):
    """Education schema."""

    degree: str
    institution: str
    field_of_study: str
    graduation_date: str
    gpa: Optional[float] = None


class Certification(BaseModel):
    """Certification schema."""

    name: str
    issuer: str
    issue_date: str
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    credential_url: Optional[HttpUrl] = None


class Resume(BaseModel):
    """Complete resume schema."""

    contact_info: ContactInfo
    summary: Optional[str] = None
    skills: List[str]
    experience: List[WorkExperience]
    education: List[Education]
    certifications: Optional[List[Certification]] = None
    languages: Optional[List[str]] = None
