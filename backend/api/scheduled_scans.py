from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from core.database import get_db
from models.user import ScheduledScan
from models.schemas import ScanCreateRequest

router = APIRouter(prefix="/api/scheduled", tags=["scheduled-scans"])


class ScheduledScanCreate(BaseModel):
    name: str
    target_url: str
    schedule_cron: str  # e.g., "0 9 * * *" for daily at 9am
    scan_config: dict


class ScheduledScanResponse(BaseModel):
    id: int
    name: str
    target_url: str
    schedule_cron: str
    is_active: bool
    last_run: datetime = None
    next_run: datetime = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/create", response_model=ScheduledScanResponse)
async def create_scheduled_scan(
    scheduled_scan: ScheduledScanCreate,
    db: Session = Depends(get_db)
):
    """Create a new scheduled scan"""
    import json
    from croniter import croniter
    from datetime import datetime

    # Validate cron expression
    try:
        base_time = datetime.now()
        iter = croniter(scheduled_scan.schedule_cron, base_time)
        next_run = iter.get_next(datetime)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid cron expression: {str(e)}")

    db_scheduled_scan = ScheduledScan(
        name=scheduled_scan.name,
        target_url=scheduled_scan.target_url,
        schedule_cron=scheduled_scan.schedule_cron,
        scan_config=json.dumps(scheduled_scan.scan_config),
        next_run=next_run
    )

    db.add(db_scheduled_scan)
    db.commit()
    db.refresh(db_scheduled_scan)

    return db_scheduled_scan


@router.get("/list", response_model=List[ScheduledScanResponse])
async def list_scheduled_scans(db: Session = Depends(get_db)):
    """List all scheduled scans"""
    scheduled_scans = db.query(ScheduledScan).order_by(ScheduledScan.created_at.desc()).all()
    return scheduled_scans


@router.put("/{schedule_id}/toggle")
async def toggle_scheduled_scan(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Enable or disable a scheduled scan"""
    scheduled_scan = db.query(ScheduledScan).filter(ScheduledScan.id == schedule_id).first()

    if not scheduled_scan:
        raise HTTPException(status_code=404, detail="Scheduled scan not found")

    scheduled_scan.is_active = not scheduled_scan.is_active
    db.commit()

    return {"message": f"Scheduled scan {'enabled' if scheduled_scan.is_active else 'disabled'}"}


@router.delete("/{schedule_id}")
async def delete_scheduled_scan(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a scheduled scan"""
    scheduled_scan = db.query(ScheduledScan).filter(ScheduledScan.id == schedule_id).first()

    if not scheduled_scan:
        raise HTTPException(status_code=404, detail="Scheduled scan not found")

    db.delete(scheduled_scan)
    db.commit()

    return {"message": "Scheduled scan deleted successfully"}
