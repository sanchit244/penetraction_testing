import requests
from typing import List, Dict
from models.schemas import VulnerabilitySchema, SeverityEnum


class XSSScanner:
    """Cross-Site Scripting vulnerability scanner"""

    PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "<svg/onload=alert('XSS')>",
        "javascript:alert('XSS')",
        "<body onload=alert('XSS')>",
        "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        "<input onfocus=alert('XSS') autofocus>",
        "<select onfocus=alert('XSS') autofocus>",
        "<textarea onfocus=alert('XSS') autofocus>",
        "<keygen onfocus=alert('XSS') autofocus>",
        "<video><source onerror='alert(\"XSS\")'>",
        "<audio src=x onerror=alert('XSS')>",
        "<details open ontoggle=alert('XSS')>",
        "'-alert('XSS')-'",
        "\"><script>alert('XSS')</script>",
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for XSS vulnerabilities"""
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
                            allow_redirects=True
                        )

                        # Check if payload is reflected in response
                        if payload in response.text or payload.replace("'", '"') in response.text:
                            vulnerabilities.append(
                                VulnerabilitySchema(
                                    name="Cross-Site Scripting (XSS)",
                                    description=f"Reflected XSS vulnerability detected in parameter '{param_name}'",
                                    severity=SeverityEnum.HIGH,
                                    cvss_score=7.3,
                                    url=url,
                                    parameter=param_name,
                                    method="GET",
                                    evidence=f"Payload reflected in response: {payload}",
                                    payload=payload,
                                    remediation="Encode all user input before rendering. Use Content Security Policy. Validate and sanitize input.",
                                    references=[
                                        "https://owasp.org/www-community/attacks/xss/",
                                        "https://cwe.mitre.org/data/definitions/79.html"
                                    ],
                                    cwe_id="CWE-79"
                                )
                            )
                            break

                    except requests.RequestException:
                        continue

        except Exception as e:
            print(f"Error scanning for XSS: {e}")

        return vulnerabilities
