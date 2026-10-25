import requests
from typing import List, Dict
from urllib.parse import urlparse, parse_qs, urlencode, urljoin
from bs4 import BeautifulSoup
from models.schemas import VulnerabilitySchema, SeverityEnum


class OpenRedirectScanner:
    """Open Redirect / Unvalidated Redirects and Forwards Scanner (CWE-601)"""

    COMMON_PARAMS = [
        "redirect", "url", "next", "return", "return_to", "returnUrl",
        "redirect_url", "redirect_uri", "goto", "dest", "destination",
        "target", "link", "r", "to", "out", "view", "checkout_url", "continue"
    ]

    PAYLOADS = [
        "https://example.com",
        "//example.com",
        "///example.com",
        "https:example.com",
        "//example.com/%2f..",
        "https://example.com#",
        "/\\example.com",
    ]

    CANARY_HOST = "example.com"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for Open Redirect vulnerabilities"""
        vulnerabilities = []
        tested_pairs = set()

        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            query_params = parse_qs(parsed.query, keep_blank_values=True)

            # Flatten parse_qs lists to single strings
            flat_params = {k: v[0] if v else "" for k, v in query_params.items()}

            # If no query params exist, test common redirect parameters
            params_to_test = flat_params.copy()
            if not params_to_test:
                for cp in self.COMMON_PARAMS[:8]:  # Test most common parameters
                    params_to_test[cp] = "https://original-placeholder.com"

            for param_name, original_val in params_to_test.items():
                for payload in self.PAYLOADS:
                    pair_key = (param_name, payload)
                    if pair_key in tested_pairs:
                        continue
                    tested_pairs.add(pair_key)

                    test_params = params_to_test.copy()
                    test_params[param_name] = payload

                    try:
                        # Test GET request without following redirects
                        response = requests.get(
                            base_url,
                            params=test_params,
                            timeout=self.timeout,
                            allow_redirects=False,
                            headers={"User-Agent": "VulnScanner/2.0 Security Auditor"}
                        )

                        evidence = None

                        # Check HTTP 3xx Redirect Location header
                        if response.status_code in (301, 302, 303, 307, 308):
                            location = response.headers.get("Location", "")
                            if self.CANARY_HOST in location:
                                evidence = f"HTTP {response.status_code} Redirect with Location header: {location}"

                        # Check Meta-refresh or JavaScript redirect in HTML body
                        if not evidence and response.text:
                            soup = BeautifulSoup(response.text, "html.parser")
                            # Meta refresh check
                            meta_refresh = soup.find("meta", attrs={"http-equiv": lambda v: v and v.lower() == "refresh"})
                            if meta_refresh:
                                content = meta_refresh.get("content", "")
                                if self.CANARY_HOST in content:
                                    evidence = f"Meta-Refresh redirect detected in HTML: {content}"

                            # JS location redirection check
                            if not evidence:
                                lower_body = response.text.lower()
                                if any(x in lower_body for x in ["window.location", "location.href", "location.replace"]):
                                    if self.CANARY_HOST in lower_body:
                                        evidence = f"Client-side JavaScript redirect matching payload found in response body"

                        if evidence:
                            vulnerabilities.append(
                                VulnerabilitySchema(
                                    name="Open Redirect (Unvalidated Redirect)",
                                    description=(
                                        f"The application accepts an untrusted destination URL in parameter '{param_name}' "
                                        f"without proper validation, allowing attackers to redirect users to arbitrary external websites."
                                    ),
                                    severity=SeverityEnum.MEDIUM,
                                    cvss_score=6.1,
                                    url=url,
                                    parameter=param_name,
                                    method="GET",
                                    evidence=evidence,
                                    payload=payload,
                                    remediation=(
                                        "1. Avoid accepting full URLs from user input for redirection.\n"
                                        "2. Use an allowlist of permitted relative paths or safe domain names.\n"
                                        "3. Validate redirect URLs against a strict whitelist before redirecting."
                                    ),
                                    references=[
                                        "https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html",
                                        "https://cwe.mitre.org/data/definitions/601.html"
                                    ],
                                    cwe_id="CWE-601"
                                )
                            )
                            # Once verified for this parameter, move to next parameter
                            break

                    except requests.RequestException:
                        continue

        except Exception as e:
            print(f"Error scanning for open redirect on {url}: {e}")

        return vulnerabilities
