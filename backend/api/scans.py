from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from core.database import get_db
from models.schemas import (
    ScanCreateRequest,
    ScanResponse,
    ScanResultsResponse,
    ScanListResponse
)
from models.scan import Scan, ScanStatus, Vulnerability
from tasks.scan_tasks import run_scan

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("/create", response_model=ScanResponse)
async def create_scan(
    request: ScanCreateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create and initiate a new vulnerability scan
    """
    # Generate unique scan ID
    scan_id = f"scan_{uuid.uuid4().hex[:12]}"

    # Create scan record
    scan = Scan(
        scan_id=scan_id,
        target_url=str(request.target_url),
        status=ScanStatus.PENDING,
        scan_config={
            "scan_depth": request.scan_depth,
            "enable_zap": request.enable_zap,
            "scan_types": request.scan_types
        }
    )

    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Queue scan task (with fallback to FastAPI background tasks if Celery is unavailable)
    try:
        run_scan.delay(
            scan_id=scan_id,
            target_url=str(request.target_url),
            scan_config=scan.scan_config
        )
    except Exception as e:
        print(f"Celery queueing failed ({e}), running directly via BackgroundTasks fallback...")
        background_tasks.add_task(
            run_scan,
            None,
            scan_id=scan_id,
            target_url=str(request.target_url),
            scan_config=scan.scan_config
        )

    return ScanResponse(
        scan_id=scan.scan_id,
        target_url=scan.target_url,
        status=scan.status,
        created_at=scan.created_at,
        progress=scan.progress,
        total_vulnerabilities=scan.total_vulnerabilities,
        critical_count=scan.critical_count,
        high_count=scan.high_count,
        medium_count=scan.medium_count,
        low_count=scan.low_count,
        info_count=scan.info_count
    )


@router.get("/history", response_model=ScanListResponse)
async def get_scan_history(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get scan history with pagination
    """
    offset = (page - 1) * page_size

    scans = db.query(Scan).order_by(Scan.created_at.desc()).offset(offset).limit(page_size).all()
    total = db.query(Scan).count()

    scan_list = [
        ScanResponse(
            scan_id=scan.scan_id,
            target_url=scan.target_url,
            status=scan.status,
            created_at=scan.created_at,
            started_at=scan.started_at,
            completed_at=scan.completed_at,
            progress=scan.progress,
            total_vulnerabilities=scan.total_vulnerabilities,
            critical_count=scan.critical_count,
            high_count=scan.high_count,
            medium_count=scan.medium_count,
            low_count=scan.low_count,
            info_count=scan.info_count,
            error_message=scan.error_message
        )
        for scan in scans
    ]

    return ScanListResponse(
        scans=scan_list,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan_status(scan_id: str, db: Session = Depends(get_db)):
    """
    Get scan status and progress
    """
    scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return ScanResponse(
        scan_id=scan.scan_id,
        target_url=scan.target_url,
        status=scan.status,
        created_at=scan.created_at,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        progress=scan.progress,
        total_vulnerabilities=scan.total_vulnerabilities,
        critical_count=scan.critical_count,
        high_count=scan.high_count,
        medium_count=scan.medium_count,
        low_count=scan.low_count,
        info_count=scan.info_count,
        error_message=scan.error_message
    )


@router.get("/{scan_id}/results", response_model=ScanResultsResponse)
async def get_scan_results(scan_id: str, db: Session = Depends(get_db)):
    """
    Get detailed scan results including all vulnerabilities
    """
    scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.status != ScanStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Scan is not completed yet. Current status: {scan.status}"
        )

    vulnerabilities = scan.vulnerabilities or []

    summary = {
        "total_vulnerabilities": scan.total_vulnerabilities,
        "critical_count": scan.critical_count,
        "high_count": scan.high_count,
        "medium_count": scan.medium_count,
        "low_count": scan.low_count,
        "info_count": scan.info_count,
        "scan_duration": str(scan.completed_at - scan.started_at) if scan.completed_at and scan.started_at else "N/A"
    }

    return ScanResultsResponse(
        scan_id=scan.scan_id,
        target_url=scan.target_url,
        status=scan.status,
        vulnerabilities=vulnerabilities,
        summary=summary,
        completed_at=scan.completed_at
    )


@router.delete("/{scan_id}")
async def delete_scan(scan_id: str, db: Session = Depends(get_db)):
    """
    Delete a scan and its results
    """
    scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Delete associated vulnerabilities
    db.query(Vulnerability).filter(Vulnerability.scan_id == scan_id).delete()

    # Delete scan
    db.delete(scan)
    db.commit()

    return {"message": f"Scan {scan_id} deleted successfully"}
