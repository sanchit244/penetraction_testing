from typing import List
import requests
from bs4 import BeautifulSoup
from models.schemas import VulnerabilitySchema, SeverityEnum


class SensitiveDataExposureScanner:
    """Sensitive Data Exposure scanner"""

    SENSITIVE_PATTERNS = {
        'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        'phone': r'\+?1?\d{9,15}',
        'ssn': r'\d{3}-\d{2}-\d{4}',
        'credit_card': r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',
        'api_key': r'(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})',
        'aws_key': r'AKIA[0-9A-Z]{16}',
        'private_key': r'-----BEGIN (RSA |DSA )?PRIVATE KEY-----',
    }

    SENSITIVE_COMMENTS = [
        'password',
        'secret',
        'token',
        'api_key',
        'credentials',
        'auth',
        'admin',
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for sensitive data exposure"""
        vulnerabilities = []

        try:
            response = requests.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Check HTML comments
            comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in str(text.parent))
            for comment in comments:
                comment_text = str(comment).lower()
                for keyword in self.SENSITIVE_COMMENTS:
                    if keyword in comment_text:
                        vulnerabilities.append(
                            VulnerabilitySchema(
                                name="Sensitive Information in Comments",
                                description=f"Sensitive keyword '{keyword}' found in HTML comments",
                                severity=SeverityEnum.MEDIUM,
                                cvss_score=5.3,
                                url=url,
                                method="GET",
                                evidence=str(comment)[:200],
                                remediation="Remove all sensitive information from HTML comments before deploying to production.",
                                references=[
                                    "https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure"
                                ],
                                cwe_id="CWE-200"
                            )
                        )
                        break

            # Check for debug information
            if 'debug' in response.text.lower() or 'stacktrace' in response.text.lower():
                vulnerabilities.append(
                    VulnerabilitySchema(
                        name="Debug Information Exposure",
                        description="Debug information or stack traces exposed in response",
                        severity=SeverityEnum.MEDIUM,
                        cvss_score=5.3,
                        url=url,
                        method="GET",
                        evidence="Debug information found in response",
                        remediation="Disable debug mode in production. Implement custom error pages.",
                        references=[
                            "https://cwe.mitre.org/data/definitions/209.html"
                        ],
                        cwe_id="CWE-209"
                    )
                )

            # Check for server information disclosure
            server_header = response.headers.get('Server', '')
            if server_header and any(tech in server_header.lower() for tech in ['apache', 'nginx', 'iis', 'tomcat']):
                vulnerabilities.append(
                    VulnerabilitySchema(
                        name="Server Information Disclosure",
                        description=f"Server header reveals technology: {server_header}",
                        severity=SeverityEnum.LOW,
                        cvss_score=3.7,
                        url=url,
                        method="GET",
                        evidence=f"Server: {server_header}",
                        remediation="Remove or obfuscate the Server header to prevent information disclosure.",
                        references=[
                            "https://cwe.mitre.org/data/definitions/200.html"
                        ],
                        cwe_id="CWE-200"
                    )
                )

        except requests.RequestException as e:
            print(f"Error scanning for sensitive data exposure: {e}")

        return vulnerabilities
