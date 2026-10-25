from typing import List
import requests
from models.schemas import VulnerabilitySchema, SeverityEnum


class CommandInjectionScanner:
    """Command Injection vulnerability scanner"""

    PAYLOADS = [
        "; ls -la",
        "| whoami",
        "& dir",
        "; cat /etc/passwd",
        "| type C:\\Windows\\win.ini",
        "`whoami`",
        "$(whoami)",
        "; ping -c 4 127.0.0.1",
        "| timeout 3",
        "&& echo vulnerable",
    ]

    EVIDENCE_PATTERNS = [
        "root",
        "administrator",
        "total ",
        "volume serial number",
        "directory of",
        "bin/bash",
        "cmd.exe",
        "pinging",
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for command injection vulnerabilities"""
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
                    test_params[param_name] = original_value + payload

                    try:
                        response = requests.get(
                            base_url,
                            params=test_params,
                            timeout=self.timeout,
                            allow_redirects=False
                        )

                        # Check for command execution evidence
                        response_lower = response.text.lower()
                        if any(pattern.lower() in response_lower for pattern in self.EVIDENCE_PATTERNS):
                            vulnerabilities.append(
                                VulnerabilitySchema(
                                    name="Command Injection",
                                    description=f"Command injection vulnerability detected in parameter '{param_name}'",
                                    severity=SeverityEnum.CRITICAL,
                                    cvss_score=9.8,
                                    url=url,
                                    parameter=param_name,
                                    method="GET",
                                    evidence=response.text[:500],
                                    payload=payload,
                                    remediation="Never pass user input directly to system commands. Use parameterized APIs. Implement strict input validation and whitelisting.",
                                    references=[
                                        "https://owasp.org/www-community/attacks/Command_Injection",
                                        "https://cwe.mitre.org/data/definitions/78.html"
                                    ],
                                    cwe_id="CWE-78"
                                )
                            )
                            break

                    except requests.RequestException:
                        continue

        except Exception as e:
            print(f"Error scanning for command injection: {e}")

        return vulnerabilities
