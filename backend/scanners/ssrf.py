import requests
from typing import List, Dict, Tuple
from urllib.parse import urlparse, parse_qs
from models.schemas import VulnerabilitySchema, SeverityEnum


class SSRFScanner:
    """Server-Side Request Forgery (SSRF) Scanner (CWE-918 / OWASP A10)"""

    COMMON_PARAMS = [
        "url", "dest", "destination", "redirect", "uri", "path", "feed",
        "fetch", "file", "download", "domain", "host", "site", "html",
        "reference", "preview", "proxy", "endpoint", "link", "webhook"
    ]

    # Probes to test for local and cloud metadata access
    PROBES: List[Tuple[str, str, str]] = [
        # (payload, probe_type, evidence_pattern)
        ("http://169.254.169.254/latest/meta-data/", "AWS/OpenStack Metadata", "ami-id"),
        ("http://169.254.169.254/latest/meta-data/", "AWS/OpenStack Metadata", "instance-id"),
        ("http://169.254.169.254/latest/meta-data/iam/security-credentials/", "AWS IAM Credentials", "security-credentials"),
        ("http://metadata.google.internal/computeMetadata/v1/", "GCP Metadata", "Metadata-Flavor"),
        ("http://127.0.0.1:22/", "Localhost SSH Service", "SSH-"),
        ("http://127.0.0.1:6379/", "Localhost Redis Service", "redis_version"),
        ("http://127.0.0.1:6379/", "Localhost Redis Service", "-ERR unknown"),
        ("http://127.0.0.1:80/", "Localhost Loopback", "127.0.0.1"),
        ("http://[::1]:80/", "IPv6 Loopback", "::1"),
    ]

    ERROR_PATTERNS = [
        "Connection refused",
        "Failed to connect to 127.0.0.1",
        "Failed to connect to localhost",
        "Connection refused to 127.0.0.1",
        "Failed to connect to 169.254.169.254",
        "cURL error 7: Failed to connect",
        "Network is unreachable",
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for Server-Side Request Forgery vulnerabilities"""
        vulnerabilities = []
        tested_pairs = set()

        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            query_params = parse_qs(parsed.query, keep_blank_values=True)

            flat_params = {k: v[0] if v else "" for k, v in query_params.items()}

            # If no parameters in URL, test against common SSRF parameter names
            params_to_test = flat_params.copy()
            if not params_to_test:
                for cp in self.COMMON_PARAMS[:8]:
                    params_to_test[cp] = "https://example.com"

            for param_name, _ in params_to_test.items():
                for payload, probe_type, expected_pattern in self.PROBES:
                    pair_key = (param_name, payload)
                    if pair_key in tested_pairs:
                        continue
                    tested_pairs.add(pair_key)

                    test_params = params_to_test.copy()
                    test_params[param_name] = payload

                    try:
                        response = requests.get(
                            base_url,
                            params=test_params,
                            timeout=self.timeout,
                            allow_redirects=False,
                            headers={"User-Agent": "VulnScanner/2.0 Security Auditor"}
                        )

                        evidence = None
                        vuln_severity = SeverityEnum.HIGH
                        cvss = 8.6

                        # 1. Direct Content Match (Full SSRF / Metadata Exposure)
                        if expected_pattern.lower() in response.text.lower():
                            evidence = f"Direct SSRF response pattern matched '{expected_pattern}' from {probe_type}. Payload: {payload}"
                            vuln_severity = SeverityEnum.CRITICAL
                            cvss = 9.8

                        # 2. Reflected internal connection errors (Blind / Semi-blind SSRF)
                        if not evidence:
                            for err in self.ERROR_PATTERNS:
                                if err.lower() in response.text.lower():
                                    evidence = f"Internal network connection error reflected in response: '{err}'. Indicates backend request attempt to: {payload}"
                                    break

                        if evidence:
                            vulnerabilities.append(
                                VulnerabilitySchema(
                                    name="Server-Side Request Forgery (SSRF)",
                                    description=(
                                        f"The application receives an external URL/resource parameter '{param_name}' and fetches it on the server-side "
                                        f"without strict network filtering, allowing internal network probing or cloud metadata access."
                                    ),
                                    severity=vuln_severity,
                                    cvss_score=cvss,
                                    url=url,
                                    parameter=param_name,
                                    method="GET",
                                    evidence=evidence,
                                    payload=payload,
                                    remediation=(
                                        "1. Implement a strict allowlist of permitted destination domains and protocols (https only).\n"
                                        "2. Block resolution to private, link-local, and loopback IP ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.169.254).\n"
                                        "3. Disable HTTP redirection on server-side HTTP client requests.\n"
                                        "4. Require IMDSv2 (session token authentication) on AWS EC2 instances."
                                    ),
                                    references=[
                                        "https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/",
                                        "https://cwe.mitre.org/data/definitions/918.html",
                                        "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html"
                                    ],
                                    cwe_id="CWE-918"
                                )
                            )
                            # Stop probing more payloads on this parameter once confirmed
                            break

                    except requests.RequestException:
                        continue

        except Exception as e:
            print(f"Error scanning for SSRF on {url}: {e}")

        return vulnerabilities
