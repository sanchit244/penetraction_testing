from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Enum
from sqlalchemy.sql import func
from core.database import Base
import enum


class ScanStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Severity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(50), unique=True, index=True, nullable=False)
    target_url = Column(String(512), nullable=False)
    status = Column(Enum(ScanStatus), default=ScanStatus.PENDING, nullable=False)

    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Results
    total_vulnerabilities = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)

    # Metadata
    scan_config = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(Integer, default=0)  # 0-100

    # Results storage
    vulnerabilities = Column(JSON, nullable=True)
    report_path = Column(String(512), nullable=True)


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(50), index=True, nullable=False)

    # Vulnerability details
    name = Column(String(256), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    cvss_score = Column(Float, nullable=True)

    # Location
    url = Column(String(512), nullable=False)
    parameter = Column(String(256), nullable=True)
    method = Column(String(10), nullable=True)  # GET, POST, etc.

    # Evidence
    evidence = Column(Text, nullable=True)
    payload = Column(Text, nullable=True)

    # Remediation
    remediation = Column(Text, nullable=True)
    references = Column(JSON, nullable=True)

    # CWE/CVE
    cwe_id = Column(String(20), nullable=True)
    cve_id = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
