import requests
from typing import List
from models.schemas import VulnerabilitySchema, SeverityEnum


class SecurityHeadersScanner:
    """Security headers vulnerability scanner"""

    REQUIRED_HEADERS = {
        'Content-Security-Policy': {
            'severity': SeverityEnum.HIGH,
            'cvss': 6.5,
            'description': 'Content Security Policy (CSP) header is missing',
            'remediation': 'Implement a Content Security Policy to prevent XSS and data injection attacks',
            'cwe': 'CWE-693'
        },
        'X-Frame-Options': {
            'severity': SeverityEnum.MEDIUM,
            'cvss': 5.3,
            'description': 'X-Frame-Options header is missing, site may be vulnerable to clickjacking',
            'remediation': 'Set X-Frame-Options to DENY or SAMEORIGIN',
            'cwe': 'CWE-1021'
        },
        'X-Content-Type-Options': {
            'severity': SeverityEnum.MEDIUM,
            'cvss': 5.0,
            'description': 'X-Content-Type-Options header is missing',
            'remediation': 'Set X-Content-Type-Options to nosniff',
            'cwe': 'CWE-693'
        },
        'Strict-Transport-Security': {
            'severity': SeverityEnum.HIGH,
            'cvss': 6.8,
            'description': 'HSTS header is missing, vulnerable to man-in-the-middle attacks',
            'remediation': 'Enable HSTS with max-age of at least 31536000 seconds',
            'cwe': 'CWE-523'
        },
        'X-XSS-Protection': {
            'severity': SeverityEnum.LOW,
            'cvss': 3.7,
            'description': 'X-XSS-Protection header is missing',
            'remediation': 'Set X-XSS-Protection to "1; mode=block"',
            'cwe': 'CWE-79'
        },
        'Referrer-Policy': {
            'severity': SeverityEnum.LOW,
            'cvss': 3.1,
            'description': 'Referrer-Policy header is missing',
            'remediation': 'Set Referrer-Policy to no-referrer or strict-origin-when-cross-origin',
            'cwe': 'CWE-200'
        },
        'Permissions-Policy': {
            'severity': SeverityEnum.LOW,
            'cvss': 2.7,
            'description': 'Permissions-Policy header is missing',
            'remediation': 'Define a Permissions-Policy to control browser features',
            'cwe': 'CWE-693'
        }
    }

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for missing security headers"""
        vulnerabilities = []

        try:
            response = requests.get(url, timeout=self.timeout, allow_redirects=True)
            response_headers = {k.lower(): v for k, v in response.headers.items()}

            for header_name, header_info in self.REQUIRED_HEADERS.items():
                if header_name.lower() not in response_headers:
                    vulnerabilities.append(
                        VulnerabilitySchema(
                            name=f"Missing Security Header: {header_name}",
                            description=header_info['description'],
                            severity=header_info['severity'],
                            cvss_score=header_info['cvss'],
                            url=url,
                            method="GET",
                            evidence=f"Header '{header_name}' not found in response",
                            remediation=header_info['remediation'],
                            references=[
                                "https://owasp.org/www-project-secure-headers/",
                                f"https://cwe.mitre.org/data/definitions/{header_info['cwe'].split('-')[1]}.html"
                            ],
                            cwe_id=header_info['cwe']
                        )
                    )

            # Check for insecure cookies
            if 'set-cookie' in response_headers:
                cookies = response_headers['set-cookie']
                if 'secure' not in cookies.lower():
                    vulnerabilities.append(
                        VulnerabilitySchema(
                            name="Insecure Cookie Configuration",
                            description="Cookies are not marked as Secure",
                            severity=SeverityEnum.MEDIUM,
                            cvss_score=5.4,
                            url=url,
                            method="GET",
                            evidence="Set-Cookie header missing Secure flag",
                            remediation="Add Secure flag to all cookies",
                            references=["https://owasp.org/www-community/controls/SecureCookieAttribute"],
                            cwe_id="CWE-614"
                        )
                    )

                if 'httponly' not in cookies.lower():
                    vulnerabilities.append(
                        VulnerabilitySchema(
                            name="HttpOnly Flag Missing",
                            description="Cookies are not marked as HttpOnly",
                            severity=SeverityEnum.MEDIUM,
                            cvss_score=5.3,
                            url=url,
                            method="GET",
                            evidence="Set-Cookie header missing HttpOnly flag",
                            remediation="Add HttpOnly flag to cookies containing session tokens",
                            references=["https://owasp.org/www-community/HttpOnly"],
                            cwe_id="CWE-1004"
                        )
                    )

        except requests.RequestException as e:
            print(f"Error scanning security headers: {e}")

        return vulnerabilities
