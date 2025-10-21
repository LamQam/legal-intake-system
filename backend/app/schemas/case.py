from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class CaseStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PENDING_DOCUMENTS = "pending_documents"
    UNDER_REVIEW = "under_review"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class CaseType(str, Enum):
    CRIMINAL = "criminal"
    CIVIL = "civil"
    FAMILY = "family"
    CORPORATE = "corporate"
    IMMIGRATION = "immigration"
    EMPLOYMENT = "employment"
    REAL_ESTATE = "real_estate"
    PERSONAL_INJURY = "personal_injury"
    OTHER = "other"

class CaseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    case_type: CaseType
    priority: CasePriority = CasePriority.MEDIUM
    jurisdiction: Optional[str] = Field(None, max_length=100)
    estimated_value: Optional[float] = Field(None, ge=0)
    client_id: Optional[int] = None  # For admin creation
    lawyer_id: Optional[int] = None
    case_data: Optional[dict] = None

class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    jurisdiction: Optional[str] = Field(None, max_length=100)
    estimated_value: Optional[float] = Field(None, ge=0)
    actual_value: Optional[float] = Field(None, ge=0)
    lawyer_id: Optional[int] = None
    case_data: Optional[dict] = None

class CaseResponse(BaseModel):
    id: int
    case_number: str
    client_id: int
    lawyer_id: Optional[int]
    title: str
    description: Optional[str]
    case_type: str
    status: CaseStatus
    priority: CasePriority
    jurisdiction: Optional[str]
    estimated_value: Optional[float]
    actual_value: Optional[float]
    case_data: Optional[dict]
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime]

    class Config:
        from_attributes = True

class CaseListResponse(BaseModel):
    cases: List[CaseResponse]
    total: int
    page: int
    size: int

class CaseFilter(BaseModel):
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    case_type: Optional[CaseType] = None
    lawyer_id: Optional[int] = None
    client_id: Optional[int] = None
    search: Optional[str] = None  # Search in title and description
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None

class CaseStats(BaseModel):
    total_cases: int
    new_cases: int
    in_progress_cases: int
    closed_cases: int
    cancelled_cases: int
    cases_by_type: dict
    cases_by_priority: dict
    average_resolution_time: Optional[float]  # in days