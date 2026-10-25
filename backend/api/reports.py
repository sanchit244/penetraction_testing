from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from core.database import get_db
from core.config import settings
from models.scan import Scan, ScanStatus
from utils.report_generator import ReportGenerator

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{scan_id}/download")
async def download_report(scan_id: str, db: Session = Depends(get_db)):
    """
    Generate and download PDF report for a completed scan
    """
    scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.status != ScanStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot generate report for incomplete scan. Status: {scan.status}"
        )

    # Check if report already exists
    if scan.report_path and os.path.exists(scan.report_path):
        return FileResponse(
            scan.report_path,
            media_type='application/pdf',
            filename=os.path.basename(scan.report_path)
        )

    # Generate new report
    report_generator = ReportGenerator(settings.REPORT_STORAGE_PATH)

    vulnerabilities = scan.vulnerabilities or []

    summary = {
        "total_vulnerabilities": scan.total_vulnerabilities,
        "critical_count": scan.critical_count,
        "high_count": scan.high_count,
        "medium_count": scan.medium_count,
        "low_count": scan.low_count,
        "info_count": scan.info_count
    }

    try:
        report_path = report_generator.generate_report(
            scan_id=scan.scan_id,
            target_url=scan.target_url,
            vulnerabilities=vulnerabilities,
            summary=summary
        )

        # Save report path to database
        scan.report_path = report_path
        db.commit()

        return FileResponse(
            report_path,
            media_type='application/pdf',
            filename=os.path.basename(report_path)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
