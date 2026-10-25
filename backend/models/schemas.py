from pydantic import BaseModel, HttpUrl, Field, validator, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ScanStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SeverityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


from urllib.parse import urlparse


class ScanCreateRequest(BaseModel):
    target_url: str
    scan_depth: Optional[int] = Field(default=2, ge=1, le=5)
    enable_zap: Optional[bool] = False
    scan_types: Optional[List[str]] = [
        "sql_injection", "xss", "csrf", "headers", "ssl",
        "xxe", "directory_traversal", "sensitive_data",
        "command_injection", "open_redirect", "ssrf"
    ]

    @field_validator('target_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = str(v).strip()
        if not (v.startswith('http://') or v.startswith('https://')):
            if v.startswith('localhost') or v.startswith('127.0.0.1'):
                v = f"http://{v}"
            else:
                v = f"https://{v}"
        parsed = urlparse(v)
        if not parsed.netloc:
            raise ValueError("URL must include a valid domain or host name (e.g. example.com)")
        return v


class VulnerabilitySchema(BaseModel):
    name: str
    description: str
    severity: SeverityEnum
    cvss_score: Optional[float] = None
    url: str
    parameter: Optional[str] = None
    method: Optional[str] = None
    evidence: Optional[str] = None
    payload: Optional[str] = None
    remediation: Optional[str] = None
    references: Optional[List[str]] = None
    cwe_id: Optional[str] = None
    cve_id: Optional[str] = None


class ScanResponse(BaseModel):
    scan_id: str
    target_url: str
    status: ScanStatusEnum
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0
    total_vulnerabilities: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class ScanResultsResponse(BaseModel):
    scan_id: str
    target_url: str
    status: ScanStatusEnum
    vulnerabilities: List[VulnerabilitySchema]
    summary: Dict[str, Any]
    completed_at: Optional[datetime] = None


class ScanListResponse(BaseModel):
    scans: List[ScanResponse]
    total: int
    page: int
    page_size: int
