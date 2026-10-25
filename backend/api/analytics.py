from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from core.database import get_db
from models.scan import Scan, ScanStatus

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_analytics(db: Session = Depends(get_db)):
    """Get dashboard analytics and statistics"""

    # Total scans
    total_scans = db.query(Scan).count()

    # Scans by status
    scans_by_status = db.query(
        Scan.status,
        func.count(Scan.id)
    ).group_by(Scan.status).all()

    status_counts = {status.value: 0 for status in ScanStatus}
    for status, count in scans_by_status:
        status_counts[status.value] = count

    # Total vulnerabilities found
    total_vulnerabilities = db.query(
        func.sum(Scan.total_vulnerabilities)
    ).scalar() or 0

    # Vulnerabilities by severity
    critical_count = db.query(
        func.sum(Scan.critical_count)
    ).scalar() or 0

    high_count = db.query(
        func.sum(Scan.high_count)
    ).scalar() or 0

    medium_count = db.query(
        func.sum(Scan.medium_count)
    ).scalar() or 0

    low_count = db.query(
        func.sum(Scan.low_count)
    ).scalar() or 0

    # Recent scans (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_scans = db.query(Scan).filter(
        Scan.created_at >= seven_days_ago
    ).count()

    # Average scan duration
    completed_scans = db.query(Scan).filter(
        Scan.status == ScanStatus.COMPLETED,
        Scan.started_at.isnot(None),
        Scan.completed_at.isnot(None)
    ).all()

    if completed_scans:
        durations = [(scan.completed_at - scan.started_at).total_seconds() for scan in completed_scans]
        avg_duration = sum(durations) / len(durations)
    else:
        avg_duration = 0

    # Most vulnerable URLs
    url_vulns = db.query(
        Scan.target_url,
        func.sum(Scan.total_vulnerabilities).label('total')
    ).filter(
        Scan.status == ScanStatus.COMPLETED
    ).group_by(
        Scan.target_url
    ).order_by(
        desc('total')
    ).limit(5).all()

    top_vulnerable_urls = [
        {"url": url, "vulnerabilities": int(total)}
        for url, total in url_vulns
    ]

    # Scans over time (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_scans = db.query(
        func.date(Scan.created_at).label('date'),
        func.count(Scan.id).label('count')
    ).filter(
        Scan.created_at >= thirty_days_ago
    ).group_by(
        func.date(Scan.created_at)
    ).all()

    scans_timeline = [
        {"date": str(date), "count": count}
        for date, count in daily_scans
    ]

    return {
        "overview": {
            "total_scans": total_scans,
            "total_vulnerabilities": int(total_vulnerabilities),
            "recent_scans_7d": recent_scans,
            "average_scan_duration_seconds": round(avg_duration, 2)
        },
        "status_distribution": status_counts,
        "severity_distribution": {
            "critical": int(critical_count),
            "high": int(high_count),
            "medium": int(medium_count),
            "low": int(low_count)
        },
        "top_vulnerable_urls": top_vulnerable_urls,
        "scans_timeline": scans_timeline
    }


@router.get("/trends")
async def get_security_trends(db: Session = Depends(get_db)):
    """Get security trends over time"""

    # Get monthly trends for the past 6 months
    six_months_ago = datetime.utcnow() - timedelta(days=180)

    monthly_trends = db.query(
        func.date_trunc('month', Scan.created_at).label('month'),
        func.count(Scan.id).label('scan_count'),
        func.sum(Scan.total_vulnerabilities).label('total_vulns'),
        func.sum(Scan.critical_count).label('critical'),
        func.sum(Scan.high_count).label('high')
    ).filter(
        Scan.created_at >= six_months_ago,
        Scan.status == ScanStatus.COMPLETED
    ).group_by(
        func.date_trunc('month', Scan.created_at)
    ).order_by(
        func.date_trunc('month', Scan.created_at)
    ).all()

    trends = [
        {
            "month": str(month),
            "scans": scan_count,
            "total_vulnerabilities": int(total_vulns or 0),
            "critical": int(critical or 0),
            "high": int(high or 0)
        }
        for month, scan_count, total_vulns, critical, high in monthly_trends
    ]

    return {
        "trends": trends
    }
