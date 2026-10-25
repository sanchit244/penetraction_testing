from typing import List, Optional
from scanners.sql_injection import SQLInjectionScanner
from scanners.xss import XSSScanner
from scanners.csrf import CSRFScanner
from scanners.security_headers import SecurityHeadersScanner
from scanners.ssl_scanner import SSLScanner
from scanners.xxe import XXEScanner
from scanners.directory_traversal import DirectoryTraversalScanner
from scanners.sensitive_data import SensitiveDataExposureScanner
from scanners.command_injection import CommandInjectionScanner
from scanners.open_redirect import OpenRedirectScanner
from scanners.ssrf import SSRFScanner
from scanners.api_security import APISecurityScanner
from scanners.business_logic import BusinessLogicScanner
from scanners.authentication import AuthenticationScanner
from scanners.advanced_injection import AdvancedInjectionScanner
from scanners.client_side import ClientSideScanner
from scanners.cloud_infrastructure import CloudInfrastructureScanner
from models.schemas import VulnerabilitySchema


class VulnerabilityScanner:
    """Main scanner orchestrator - Enhanced with 17 advanced scanners"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.scanners = {
            # Original scanners
            'sql_injection': SQLInjectionScanner(timeout),
            'xss': XSSScanner(timeout),
            'csrf': CSRFScanner(timeout),
            'headers': SecurityHeadersScanner(timeout),
            'ssl': SSLScanner(timeout),
            'xxe': XXEScanner(timeout),
            'directory_traversal': DirectoryTraversalScanner(timeout),
            'sensitive_data': SensitiveDataExposureScanner(timeout),
            'command_injection': CommandInjectionScanner(timeout),
            'open_redirect': OpenRedirectScanner(timeout),
            'ssrf': SSRFScanner(timeout),

            # Advanced scanners - High Impact
            'api_security': APISecurityScanner(timeout),
            'business_logic': BusinessLogicScanner(timeout),
            'authentication': AuthenticationScanner(timeout),

            # Advanced scanners - Medium Impact
            'advanced_injection': AdvancedInjectionScanner(timeout),
            'client_side': ClientSideScanner(timeout),
            'cloud_infrastructure': CloudInfrastructureScanner(timeout),
        }

    def scan(
        self,
        url: str,
        scan_types: Optional[List[str]] = None,
        depth: int = 2
    ) -> List[VulnerabilitySchema]:
        """
        Run selected vulnerability scans against target URL

        Args:
            url: Target URL to scan
            scan_types: List of scan types to run (None = all)
            depth: Scan depth (1-5)

        Returns:
            List of detected vulnerabilities
        """
        if scan_types is None:
            scan_types = list(self.scanners.keys())

        vulnerabilities = []

        for scan_type in scan_types:
            if scan_type in self.scanners:
                try:
                    print(f"Running {scan_type} scan...")
                    results = self.scanners[scan_type].scan(url, depth)
                    vulnerabilities.extend(results)
                    print(f"{scan_type} scan completed: {len(results)} vulnerabilities found")
                except Exception as e:
                    print(f"Error running {scan_type} scan: {e}")

        return vulnerabilities

    def get_severity_counts(self, vulnerabilities: List[VulnerabilitySchema]) -> dict:
        """Count vulnerabilities by severity"""
        counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0
        }

        for vuln in vulnerabilities:
            counts[vuln.severity.value] += 1

        return counts
