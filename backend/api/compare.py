from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json

from core.database import get_db
from models.scan import Scan, Vulnerability

router = APIRouter(prefix="/api/compare", tags=["comparison"])


@router.get("/{scan_id_1}/vs/{scan_id_2}")
async def compare_scans(
    scan_id_1: str,
    scan_id_2: str,
    db: Session = Depends(get_db)
):
    """Compare two scans and show differences"""

    # Get both scans
    scan1 = db.query(Scan).filter(Scan.scan_id == scan_id_1).first()
    scan2 = db.query(Scan).filter(Scan.scan_id == scan_id_2).first()

    if not scan1 or not scan2:
        raise HTTPException(status_code=404, detail="One or both scans not found")

    # Get vulnerabilities
    vulns1 = scan1.vulnerabilities or []
    vulns2 = scan2.vulnerabilities or []

    # Create sets of vulnerability signatures
    vulns1_sigs = set()
    for v in vulns1:
        sig = f"{v.get('name', '')}:{v.get('url', '')}:{v.get('parameter', '')}"
        vulns1_sigs.add(sig)

    vulns2_sigs = set()
    for v in vulns2:
        sig = f"{v.get('name', '')}:{v.get('url', '')}:{v.get('parameter', '')}"
        vulns2_sigs.add(sig)

    # Find differences
    new_vulnerabilities = vulns2_sigs - vulns1_sigs
    fixed_vulnerabilities = vulns1_sigs - vulns2_sigs
    common_vulnerabilities = vulns1_sigs & vulns2_sigs

    # Get detailed vulnerability info
    new_vulns_detail = [v for v in vulns2 if f"{v.get('name', '')}:{v.get('url', '')}:{v.get('parameter', '')}" in new_vulnerabilities]
    fixed_vulns_detail = [v for v in vulns1 if f"{v.get('name', '')}:{v.get('url', '')}:{v.get('parameter', '')}" in fixed_vulnerabilities]

    return {
        "scan_1": {
            "scan_id": scan1.scan_id,
            "target_url": scan1.target_url,
            "created_at": scan1.created_at,
            "total_vulnerabilities": scan1.total_vulnerabilities
        },
        "scan_2": {
            "scan_id": scan2.scan_id,
            "target_url": scan2.target_url,
            "created_at": scan2.created_at,
            "total_vulnerabilities": scan2.total_vulnerabilities
        },
        "comparison": {
            "new_vulnerabilities_count": len(new_vulnerabilities),
            "fixed_vulnerabilities_count": len(fixed_vulnerabilities),
            "common_vulnerabilities_count": len(common_vulnerabilities),
            "new_vulnerabilities": new_vulns_detail,
            "fixed_vulnerabilities": fixed_vulns_detail
        },
        "summary": {
            "status": "improved" if len(fixed_vulnerabilities) > len(new_vulnerabilities) else "degraded" if len(new_vulnerabilities) > len(fixed_vulnerabilities) else "unchanged",
            "change_percentage": round(((len(new_vulnerabilities) - len(fixed_vulnerabilities)) / max(len(vulns1_sigs), 1)) * 100, 2)
        }
    }
