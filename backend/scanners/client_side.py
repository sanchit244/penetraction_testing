"""
Client-Side Security Scanner - DOM XSS, client storage, third-party scripts
"""
import re
import json
from typing import List, Dict
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from models.schemas import VulnerabilitySchema, SeverityEnum


class ClientSideScanner:
    """Client-side security vulnerability testing"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def scan(self, url: str, depth: int = 2) -> List[VulnerabilitySchema]:
        """Run all client-side security checks"""
        vulnerabilities = []

        vulnerabilities.extend(self._test_dom_xss(url))
        vulnerabilities.extend(self._test_client_storage(url))
        vulnerabilities.extend(self._test_third_party_scripts(url))
        vulnerabilities.extend(self._test_subresource_integrity(url))
        vulnerabilities.extend(self._test_websocket_security(url))
        vulnerabilities.extend(self._test_postmessage_vulnerabilities(url))
        vulnerabilities.extend(self._test_client_side_validation(url))

        return vulnerabilities

    def _test_dom_xss(self, url: str) -> List[VulnerabilitySchema]:
        """Test for DOM-based XSS vulnerabilities"""
        vulnerabilities = []

        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Find all scripts
            scripts = soup.find_all('script')

            # Dangerous DOM sinks
            dangerous_sinks = [
                r'\.innerHTML\s*=',
                r'\.outerHTML\s*=',
                r'document\.write\(',
                r'document\.writeln\(',
                r'eval\(',
                r'setTimeout\(',
                r'setInterval\(',
                r'\.location\s*=',
                r'\.href\s*=',
                r'\.src\s*=',
            ]

            # Sources from URL
            url_sources = [
                r'location\.hash',
                r'location\.search',
                r'window\.location',
                r'document\.URL',
                r'document\.documentURI',
                r'document\.referrer',
            ]

            for script in scripts:
                script_content = script.string or ''

                # Check for dangerous patterns
                for sink in dangerous_sinks:
                    if re.search(sink, script_content):
                        # Check if source is from URL
                        for source in url_sources:
                            if re.search(source, script_content):
                                vulnerabilities.append(VulnerabilitySchema(
                                    type="dom_xss",
                                    severity=SeverityEnum.HIGH,
                                    url=url,
                                    description=f"Potential DOM XSS: URL data flows to dangerous sink",
                                    evidence=f"Pattern found: {source} -> {sink}",
                                    remediation="Sanitize user input before inserting into DOM, use textContent instead of innerHTML",
                                    cwe="CWE-79",
                                    cvss_score=7.5
                                ))
                                break

                # Check for dangerous eval patterns
                if 'eval(' in script_content:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="dangerous_eval_usage",
                        severity=SeverityEnum.MEDIUM,
                        url=url,
                        description="Use of eval() function detected",
                        evidence="eval() can execute arbitrary JavaScript",
                        remediation="Avoid eval(), use JSON.parse() or safe alternatives",
                        cwe="CWE-95",
                        cvss_score=5.3
                    ))

        except Exception:
            pass

        return vulnerabilities

    def _test_client_storage(self, url: str) -> List[VulnerabilitySchema]:
        """Test for sensitive data in client-side storage"""
        vulnerabilities = []

        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Find all scripts
            scripts = soup.find_all('script')

            # Sensitive data patterns
            sensitive_patterns = [
                (r'localStorage\.setItem\(["\'].*password', 'password'),
                (r'localStorage\.setItem\(["\'].*token', 'token'),
                (r'localStorage\.setItem\(["\'].*secret', 'secret'),
                (r'localStorage\.setItem\(["\'].*apikey', 'api key'),
                (r'localStorage\.setItem\(["\'].*credit', 'credit card'),
                (r'sessionStorage\.setItem\(["\'].*password', 'password'),
                (r'sessionStorage\.setItem\(["\'].*token', 'token'),
            ]

            for script in scripts:
                script_content = script.string or ''

                for pattern, data_type in sensitive_patterns:
                    if re.search(pattern, script_content, re.IGNORECASE):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="sensitive_data_in_storage",
                            severity=SeverityEnum.HIGH,
                            url=url,
                            description=f"Sensitive data ({data_type}) stored in localStorage/sessionStorage",
                            evidence=f"Pattern found: {pattern}",
                            remediation="Store sensitive data server-side, use httpOnly cookies",
                            cwe="CWE-312",
                            cvss_score=7.5
                        ))

                # Check for unencrypted storage
                if 'localStorage.setItem' in script_content or 'sessionStorage.setItem' in script_content:
                    if 'encrypt' not in script_content.lower() and 'crypto' not in script_content.lower():
                        vulnerabilities.append(VulnerabilitySchema(
                            type="unencrypted_client_storage",
                            severity=SeverityEnum.MEDIUM,
                            url=url,
                            description="Data stored in client storage without encryption",
                            evidence="localStorage/sessionStorage used without encryption",
                            remediation="Encrypt sensitive data before storing client-side",
                            cwe="CWE-311",
                            cvss_score=5.3
                        ))
                        break

        except Exception:
            pass

        return vulnerabilities

    def _test_third_party_scripts(self, url: str) -> List[VulnerabilitySchema]:
        """Test for vulnerable third-party scripts"""
        vulnerabilities = []

        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Find all external scripts
            scripts = soup.find_all('script', src=True)

            # Known vulnerable CDN patterns
            vulnerable_patterns = [
                (r'jquery-1\.[0-7]', 'jQuery < 1.9 (XSS vulnerabilities)'),
                (r'jquery-2\.[0-2]', 'jQuery < 2.2 (XSS vulnerabilities)'),
                (r'angular\.js/1\.[0-5]', 'AngularJS < 1.6 (sandbox bypass)'),
                (r'lodash\.js/[0-3]\.', 'Lodash < 4.17.11 (prototype pollution)'),
                (r'moment\.js/2\.(0|1[0-8])', 'Moment.js < 2.19.3 (ReDoS)'),
            ]

            for script in scripts:
                src = script.get('src', '')

                # Check for HTTP (unencrypted) CDN
                if src.startswith('http://'):
                    vulnerabilities.append(VulnerabilitySchema(
                        type="unencrypted_cdn_resource",
                        severity=SeverityEnum.HIGH,
                        url=url,
                        description="Third-party script loaded over HTTP",
                        evidence=f"Insecure resource: {src}",
                        remediation="Use HTTPS for all external resources",
                        cwe="CWE-319",
                        cvss_score=7.5
                    ))

                # Check for vulnerable versions
                for pattern, description in vulnerable_patterns:
                    if re.search(pattern, src, re.IGNORECASE):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="vulnerable_third_party_library",
                            severity=SeverityEnum.HIGH,
                            url=url,
                            description=f"Vulnerable library detected: {description}",
                            evidence=f"Script source: {src}",
                            remediation="Update to latest secure version",
                            cwe="CWE-1104",
                            cvss_score=7.5
                        ))

                # Check for inline event handlers (XSS risk)
                if script.get('onerror') or script.get('onload'):
                    vulnerabilities.append(VulnerabilitySchema(
                        type="inline_event_handler",
                        severity=SeverityEnum.MEDIUM,
                        url=url,
                        description="Inline event handlers on script tags",
                        evidence="onerror/onload attributes can be exploited",
                        remediation="Use addEventListener() instead of inline handlers",
                        cwe="CWE-79",
                        cvss_score=5.3
                    ))

        except Exception:
            pass

        return vulnerabilities

    def _test_subresource_integrity(self, url: str) -> List[VulnerabilitySchema]:
        """Test for Subresource Integrity (SRI) on external resources"""
        vulnerabilities = []

        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Check scripts
            external_scripts = soup.find_all('script', src=True)
            for script in external_scripts:
                src = script.get('src', '')
                # Check if it's a CDN resource
                if any(cdn in src for cdn in ['cdn.', 'cloudflare', 'unpkg', 'jsdelivr']):
                    if not script.get('integrity'):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="missing_sri",
                            severity=SeverityEnum.MEDIUM,
                            url=url,
                            description="External script lacks Subresource Integrity (SRI)",
                            evidence=f"CDN script without SRI: {src}",
                            remediation="Add integrity attribute to all CDN resources",
                            cwe="CWE-353",
                            cvss_score=5.3
                        ))

            # Check stylesheets
            external_styles = soup.find_all('link', rel='stylesheet', href=True)
            for style in external_styles:
                href = style.get('href', '')
                if any(cdn in href for cdn in ['cdn.', 'cloudflare', 'unpkg', 'jsdelivr']):
                    if not style.get('integrity'):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="missing_sri_stylesheet",
                            severity=SeverityEnum.LOW,
                            url=url,
                            description="External stylesheet lacks SRI",
                            evidence=f"CDN stylesheet without SRI: {href}",
                            remediation="Add integrity attribute to external stylesheets",
                            cwe="CWE-353",
                            cvss_score=3.7
                        ))

        except Exception:
            pass

        return vulnerabilities

    def _test_websocket_security(self, url: str) -> List[VulnerabilitySchema]:
        """Test for WebSocket security issues"""
        vulnerabilities = []

        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')

            scripts = soup.find_all('script')

            for script in scripts:
                script_content = script.string or ''

                # Check for WebSocket usage
                ws_patterns = [
                    (r'new\s+WebSocket\(["\']ws://', 'Unencrypted WebSocket (ws://)'),
                    (r'WebSocket\(["\']ws://', 'Unencrypted WebSocket connection'),
                ]

                for pattern, description in ws_patterns:
                    if re.search(pattern, script_content):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="insecure_websocket",
                            severity=SeverityEnum.HIGH,
                            url=url,
                            description=description,
                            evidence="WebSocket connection not encrypted",
                            remediation="Use wss:// instead of ws:// for encrypted connections",
                            cwe="CWE-319",
                            cvss_score=7.5
                        ))

                # Check for missing origin validation
                if 'new WebSocket(' in script_content or 'WebSocket(' in script_content:
                    if 'origin' not in script_content.lower():
                        vulnerabilities.append(VulnerabilitySchema(
                            type="websocket_no_origin_check",
                            severity=SeverityEnum.MEDIUM,
                            url=url,
                            description="WebSocket connection without origin validation",
                            evidence="No origin checking detected in WebSocket code",
                            remediation="Validate origin header in WebSocket handshake",
                            cwe="CWE-346",
                            cvss_score=5.3
                        ))

        except Exception:
            pass

        return vulnerabilities

    def _test_postmessage_vulnerabilities(self, url: str) -> List[VulnerabilitySchema]:
        """Test for postMessage security issues"""
        vulnerabilities = []

        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')

            scripts = soup.find_all('script')

            for script in scripts:
                script_content = script.string or ''

                # Check for postMessage usage
                if 'postMessage' in script_content:
                    # Check for wildcard origin
                    if re.search(r'postMessage\([^,]+,\s*["\']?\*["\']?\)', script_content):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="postmessage_wildcard_origin",
                            severity=SeverityEnum.HIGH,
                            url=url,
                            description="postMessage with wildcard (*) target origin",
                            evidence="Sensitive data may be sent to any origin",
                            remediation="Specify exact target origin instead of '*'",
                            cwe="CWE-942",
                            cvss_score=7.5
                        ))

                # Check for message event listener
                if 'addEventListener' in script_content and 'message' in script_content:
                    # Check for missing origin validation
                    if not re.search(r'event\.origin\s*[!=]=', script_content):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="postmessage_no_origin_check",
                            severity=SeverityEnum.HIGH,
                            url=url,
                            description="Message event listener without origin validation",
                            evidence="postMessage receiver doesn't validate sender origin",
                            remediation="Always validate event.origin before processing messages",
                            cwe="CWE-346",
                            cvss_score=7.5
                        ))

        except Exception:
            pass

        return vulnerabilities

    def _test_client_side_validation(self, url: str) -> List[VulnerabilitySchema]:
        """Test for client-side only validation"""
        vulnerabilities = []

        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Find forms
            forms = soup.find_all('form')

            for form in forms:
                has_client_validation = False
                has_novalidate = form.get('novalidate') is not None

                # Check for HTML5 validation
                inputs = form.find_all(['input', 'textarea', 'select'])
                for inp in inputs:
                    if any(attr in inp.attrs for attr in ['required', 'pattern', 'min', 'max', 'maxlength']):
                        has_client_validation = True
                        break

                # Check for JavaScript validation
                if form.get('onsubmit') or soup.find('script'):
                    scripts = soup.find_all('script')
                    for script in scripts:
                        script_content = script.string or ''
                        if any(word in script_content for word in ['validate', 'validation', 'checkForm']):
                            has_client_validation = True
                            break

                if has_client_validation and not has_novalidate:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="client_side_validation_only",
                        severity=SeverityEnum.MEDIUM,
                        url=url,
                        description="Form relies on client-side validation only",
                        evidence="Client-side validation can be bypassed",
                        remediation="Always validate input server-side, client validation is for UX only",
                        cwe="CWE-602",
                        cvss_score=5.3
                    ))
                    break

        except Exception:
            pass

        return vulnerabilities
