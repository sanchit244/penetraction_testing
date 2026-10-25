import requests
from typing import List
from models.schemas import VulnerabilitySchema, SeverityEnum


class CSRFScanner:
    """Cross-Site Request Forgery vulnerability scanner"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for CSRF vulnerabilities"""
        vulnerabilities = []

        try:
            response = requests.get(url, timeout=self.timeout)

            # Check for CSRF token in common locations
            has_csrf_token = False
            csrf_indicators = [
                'csrf', 'csrftoken', '_token', 'authenticity_token',
                'anti-forgery', 'xsrf', '__requestverificationtoken'
            ]

            # Check in cookies
            for cookie_name in response.cookies.keys():
                if any(indicator in cookie_name.lower() for indicator in csrf_indicators):
                    has_csrf_token = True
                    break

            # Check in HTML content
            if not has_csrf_token:
                content_lower = response.text.lower()
                for indicator in csrf_indicators:
                    if indicator in content_lower:
                        has_csrf_token = True
                        break

            # Check for forms without CSRF protection
            if '<form' in response.text.lower() and not has_csrf_token:
                vulnerabilities.append(
                    VulnerabilitySchema(
                        name="Missing CSRF Protection",
                        description="Forms detected without apparent CSRF token protection",
                        severity=SeverityEnum.HIGH,
                        cvss_score=6.5,
                        url=url,
                        method="GET",
                        evidence="HTML forms found without CSRF tokens",
                        remediation="Implement CSRF tokens for all state-changing operations. Use SameSite cookie attribute.",
                        references=[
                            "https://owasp.org/www-community/attacks/csrf",
                            "https://cwe.mitre.org/data/definitions/352.html"
                        ],
                        cwe_id="CWE-352"
                    )
                )

            # Check SameSite cookie attribute
            if response.cookies:
                for cookie in response.cookies:
                    cookie_str = str(cookie)
                    if 'samesite' not in cookie_str.lower():
                        vulnerabilities.append(
                            VulnerabilitySchema(
                                name="Missing SameSite Cookie Attribute",
                                description=f"Cookie '{cookie.name}' missing SameSite attribute",
                                severity=SeverityEnum.MEDIUM,
                                cvss_score=5.3,
                                url=url,
                                parameter=cookie.name,
                                method="GET",
                                evidence=f"Cookie '{cookie.name}' does not have SameSite attribute",
                                remediation="Set SameSite attribute to 'Lax' or 'Strict' for all cookies",
                                references=["https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite"],
                                cwe_id="CWE-352"
                            )
                        )

        except requests.RequestException as e:
            print(f"Error scanning for CSRF: {e}")

        return vulnerabilities
