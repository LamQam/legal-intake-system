from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models import Case, User, Lawyer
from app.schemas.case import (
    CaseCreate, CaseUpdate, CaseResponse, CaseListResponse,
    CaseFilter, CaseStats, CaseStatus, CasePriority, CaseType
)

logger = logging.getLogger(__name__)

router = APIRouter()

def generate_case_number() -> str:
    """Generate a unique case number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    # In a real application, you'd check for uniqueness in the database
    return f"CAS-{timestamp}-{datetime.now().microsecond}"

@router.post("/", response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    db: Session = Depends(get_db)
):
    """Create a new case"""
    try:
        # If client_id not provided, create a temporary client
        if not case_data.client_id:
            # This would typically come from the authenticated user
            # For now, create a placeholder
            client = User(
                phone=f"temp_{datetime.now().timestamp()}",
                full_name="Pending Client Info",
                email=f"temp_{datetime.now().timestamp()}@temp.local"
            )
            db.add(client)
            db.commit()
            db.refresh(client)
            client_id = client.id
        else:
            client_id = case_data.client_id

        # Create the case
        db_case = Case(
            case_number=generate_case_number(),
            client_id=client_id,
            lawyer_id=case_data.lawyer_id,
            title=case_data.title,
            description=case_data.description,
            case_type=case_data.case_type.value,
            priority=case_data.priority,
            jurisdiction=case_data.jurisdiction,
            estimated_value=case_data.estimated_value,
            case_data=case_data.case_data or {}
        )

        db.add(db_case)
        db.commit()
        db.refresh(db_case)

        logger.info(f"Created case {db_case.case_number} for client {client_id}")
        return db_case

    except Exception as e:
        logger.error(f"Error creating case: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create case")

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific case by ID"""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return case

@router.get("/", response_model=CaseListResponse)
async def list_cases(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[CaseStatus] = None,
    priority: Optional[CasePriority] = None,
    case_type: Optional[CaseType] = None,
    lawyer_id: Optional[int] = None,
    client_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List cases with filtering and pagination"""
    try:
        # Build query
        query = db.query(Case)

        # Apply filters
        if status:
            query = query.filter(Case.status == status)
        if priority:
            query = query.filter(Case.priority == priority)
        if case_type:
            query = query.filter(Case.case_type == case_type.value)
        if lawyer_id:
            query = query.filter(Case.lawyer_id == lawyer_id)
        if client_id:
            query = query.filter(Case.client_id == client_id)

        # Apply search
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Case.title.ilike(search_filter),
                    Case.description.ilike(search_filter),
                    Case.case_number.ilike(search_filter)
                )
            )

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        cases = query.order_by(desc(Case.created_at)).offset((page - 1) * size).limit(size).all()

        return CaseListResponse(
            cases=cases,
            total=total,
            page=page,
            size=size
        )

    except Exception as e:
        logger.error(f"Error listing cases: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve cases")

@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    case_update: CaseUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing case"""
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Update fields
        update_data = case_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(case, field):
                setattr(case, field, value)

        # Update timestamp
        case.updated_at = datetime.utcnow()

        # If status is being set to closed, set closed_at
        if case_update.status == CaseStatus.CLOSED and case.status != CaseStatus.CLOSED:
            case.closed_at = datetime.utcnow()

        db.commit()
        db.refresh(case)

        logger.info(f"Updated case {case.case_number}")
        return case

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating case: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update case")

@router.delete("/{case_id}")
async def delete_case(
    case_id: int,
    db: Session = Depends(get_db)
):
    """Delete a case (soft delete by changing status)"""
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Soft delete by changing status
        case.status = CaseStatus.CANCELLED
        case.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"Deleted case {case.case_number}")
        return {"message": "Case deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting case: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete case")

@router.get("/stats/summary", response_model=CaseStats)
async def get_case_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get case statistics for the specified period"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Base query for the period
        base_query = db.query(Case).filter(Case.created_at >= start_date)

        # Basic counts
        total_cases = base_query.count()
        new_cases = base_query.filter(Case.status == CaseStatus.NEW).count()
        in_progress_cases = base_query.filter(Case.status == CaseStatus.IN_PROGRESS).count()
        closed_cases = base_query.filter(Case.status == CaseStatus.CLOSED).count()
        cancelled_cases = base_query.filter(Case.status == CaseStatus.CANCELLED).count()

        # Cases by type
        cases_by_type = {}
        for case_type in CaseType:
            count = base_query.filter(Case.case_type == case_type.value).count()
            if count > 0:
                cases_by_type[case_type.value] = count

        # Cases by priority
        cases_by_priority = {}
        for priority in CasePriority:
            count = base_query.filter(Case.priority == priority).count()
            if count > 0:
                cases_by_priority[priority.value] = count

        # Average resolution time (for closed cases in the period)
        closed_cases_query = db.query(Case).filter(
            Case.status == CaseStatus.CLOSED,
            Case.closed_at >= start_date,
            Case.created_at >= start_date
        )

        resolution_times = []
        for case in closed_cases_query.all():
            if case.closed_at and case.created_at:
                days = (case.closed_at - case.created_at).days
                resolution_times.append(days)

        average_resolution_time = None
        if resolution_times:
            average_resolution_time = sum(resolution_times) / len(resolution_times)

        return CaseStats(
            total_cases=total_cases,
            new_cases=new_cases,
            in_progress_cases=in_progress_cases,
            closed_cases=closed_cases,
            cancelled_cases=cancelled_cases,
            cases_by_type=cases_by_type,
            cases_by_priority=cases_by_priority,
            average_resolution_time=average_resolution_time
        )

    except Exception as e:
        logger.error(f"Error getting case stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve case statistics")

@router.post("/{case_id}/assign")
async def assign_case_to_lawyer(
    case_id: int,
    lawyer_id: int,
    db: Session = Depends(get_db)
):
    """Assign a case to a lawyer"""
    try:
        # Verify case exists
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")

        # Verify lawyer exists and is available
        lawyer = db.query(Lawyer).filter(Lawyer.id == lawyer_id).first()
        if not lawyer:
            raise HTTPException(status_code=404, detail="Lawyer not found")

        if not lawyer.is_available:
            raise HTTPException(status_code=400, detail="Lawyer is not available")

        # Assign the case
        case.lawyer_id = lawyer_id
        case.status = CaseStatus.IN_PROGRESS
        case.updated_at = datetime.utcnow()

        # Update lawyer's case count
        lawyer.total_cases += 1

        db.commit()

        logger.info(f"Assigned case {case.case_number} to lawyer {lawyer_id}")
        return {"message": "Case assigned successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning case: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to assign case")