"""
VulnScanner Pro - Advanced Security Testing Scanners
Version: 2.0
Total Scanners: 17

This package contains comprehensive vulnerability detection modules.
"""

from .scanner import VulnerabilityScanner

# Original Scanners
from .sql_injection import SQLInjectionScanner
from .xss import XSSScanner
from .csrf import CSRFScanner
from .security_headers import SecurityHeadersScanner
from .ssl_scanner import SSLScanner
from .xxe import XXEScanner
from .directory_traversal import DirectoryTraversalScanner
from .sensitive_data import SensitiveDataExposureScanner
from .command_injection import CommandInjectionScanner
from .open_redirect import OpenRedirectScanner
from .ssrf import SSRFScanner

# Advanced Scanners - High Impact
from .api_security import APISecurityScanner
from .business_logic import BusinessLogicScanner
from .authentication import AuthenticationScanner

# Advanced Scanners - Medium Impact
from .advanced_injection import AdvancedInjectionScanner
from .client_side import ClientSideScanner
from .cloud_infrastructure import CloudInfrastructureScanner

__all__ = [
    'VulnerabilityScanner',
    # Original
    'SQLInjectionScanner',
    'XSSScanner',
    'CSRFScanner',
    'SecurityHeadersScanner',
    'SSLScanner',
    'XXEScanner',
    'DirectoryTraversalScanner',
    'SensitiveDataExposureScanner',
    'CommandInjectionScanner',
    'OpenRedirectScanner',
    'SSRFScanner',
    # Advanced
    'APISecurityScanner',
    'BusinessLogicScanner',
    'AuthenticationScanner',
    'AdvancedInjectionScanner',
    'ClientSideScanner',
    'CloudInfrastructureScanner',
]

__version__ = '2.0.0'
