from datetime import datetime
from tasks.celery_app import celery_app
from scanners.scanner import VulnerabilityScanner
from models.scan import Scan, ScanStatus, Vulnerability
from core.database import SessionLocal
from sqlalchemy.orm import Session
import traceback


@celery_app.task(bind=True, name='tasks.run_scan')
def run_scan(self, scan_id: str, target_url: str, scan_config: dict):
    """
    Celery task to run vulnerability scan

    Args:
        scan_id: Unique scan identifier
        target_url: URL to scan
        scan_config: Scan configuration (depth, scan_types, etc.)
    """
    db = SessionLocal()

    try:
        # Update scan status to running
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if not scan:
            return {"error": "Scan not found"}

        scan.status = ScanStatus.RUNNING
        scan.started_at = datetime.utcnow()
        scan.progress = 5
        db.commit()

        # Initialize scanner
        scanner = VulnerabilityScanner(timeout=30)

        # Extract scan configuration
        depth = scan_config.get('scan_depth', 2)
        scan_types = scan_config.get('scan_types', [
            'sql_injection', 'xss', 'csrf', 'headers', 'ssl',
            'xxe', 'directory_traversal', 'sensitive_data',
            'command_injection', 'open_redirect', 'ssrf'
        ])

        # Update progress
        scan.progress = 10
        db.commit()

        # Run vulnerability scans
        vulnerabilities = scanner.scan(
            url=target_url,
            scan_types=scan_types,
            depth=depth
        )

        # Update progress
        scan.progress = 70
        db.commit()

        # Store vulnerabilities in database
        vuln_list = []
        for vuln in vulnerabilities:
            db_vuln = Vulnerability(
                scan_id=scan_id,
                name=vuln.name,
                description=vuln.description,
                severity=vuln.severity,
                cvss_score=vuln.cvss_score,
                url=vuln.url,
                parameter=vuln.parameter,
                method=vuln.method,
                evidence=vuln.evidence,
                payload=vuln.payload,
                remediation=vuln.remediation,
                references=vuln.references,
                cwe_id=vuln.cwe_id,
                cve_id=vuln.cve_id
            )
            db.add(db_vuln)
            vuln_list.append(vuln.dict())

        # Update progress
        scan.progress = 85
        db.commit()

        # Get severity counts
        severity_counts = scanner.get_severity_counts(vulnerabilities)

        # Update scan with results
        scan.status = ScanStatus.COMPLETED
        scan.completed_at = datetime.utcnow()
        scan.progress = 100
        scan.total_vulnerabilities = len(vulnerabilities)
        scan.critical_count = severity_counts['critical']
        scan.high_count = severity_counts['high']
        scan.medium_count = severity_counts['medium']
        scan.low_count = severity_counts['low']
        scan.info_count = severity_counts['info']
        scan.vulnerabilities = vuln_list

        db.commit()

        return {
            "scan_id": scan_id,
            "status": "completed",
            "total_vulnerabilities": len(vulnerabilities),
            "severity_counts": severity_counts
        }

    except Exception as e:
        # Handle errors
        print(f"Error in scan task: {str(e)}")
        print(traceback.format_exc())

        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if scan:
            scan.status = ScanStatus.FAILED
            scan.completed_at = datetime.utcnow()
            scan.error_message = str(e)
            scan.progress = 0
            db.commit()

        return {"error": str(e)}

    finally:
        db.close()


@celery_app.task(name='tasks.cleanup_old_scans')
def cleanup_old_scans():
    """Periodic task to clean up old scan results"""
    db = SessionLocal()
    try:
        # Implementation for cleaning old scans
        # Delete scans older than MAX_REPORT_AGE_DAYS
        pass
    finally:
        db.close()
