"""
Authentication & Session Security Scanner - Tests MFA, session management, password policies
"""
import re
import hashlib
import time
from typing import List, Dict
from urllib.parse import urljoin, parse_qs, urlparse
import requests
from models.schemas import VulnerabilitySchema, SeverityEnum


class AuthenticationScanner:
    """Authentication and session security testing"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def scan(self, url: str, depth: int = 2) -> List[VulnerabilitySchema]:
        """Run all authentication security checks"""
        vulnerabilities = []

        vulnerabilities.extend(self._test_weak_passwords(url))
        vulnerabilities.extend(self._test_session_fixation(url))
        vulnerabilities.extend(self._test_session_hijacking(url))
        vulnerabilities.extend(self._test_mfa_bypass(url))
        vulnerabilities.extend(self._test_password_reset(url))
        vulnerabilities.extend(self._test_account_enumeration(url))
        vulnerabilities.extend(self._test_session_timeout(url))
        vulnerabilities.extend(self._test_brute_force_protection(url))
        vulnerabilities.extend(self._test_credential_stuffing(url))

        return vulnerabilities

    def _test_weak_passwords(self, url: str) -> List[VulnerabilitySchema]:
        """Test for weak password policy"""
        vulnerabilities = []

        register_endpoints = ['/register', '/signup', '/api/register', '/api/users/create']

        weak_passwords = [
            '123456',
            'password',
            'admin',
            'test',
            'qwerty',
            '111111',
            'abc123'
        ]

        for endpoint in register_endpoints:
            test_url = urljoin(url, endpoint)

            for weak_pass in weak_passwords:
                try:
                    resp = self.session.post(
                        test_url,
                        json={
                            'username': f'test_{int(time.time())}',
                            'email': f'test_{int(time.time())}@example.com',
                            'password': weak_pass
                        },
                        timeout=self.timeout,
                        verify=False
                    )

                    if resp.status_code in [200, 201]:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="weak_password_policy",
                            severity=SeverityEnum.HIGH,
                            url=test_url,
                            description=f"Weak password accepted: '{weak_pass}'",
                            evidence="No password complexity requirements enforced",
                            remediation="Enforce strong password policy: min 8 chars, uppercase, lowercase, numbers, symbols",
                            cwe="CWE-521",
                            cvss_score=7.5
                        ))
                        break

                except Exception:
                    continue

            if vulnerabilities:
                break

        return vulnerabilities

    def _test_session_fixation(self, url: str) -> List[VulnerabilitySchema]:
        """Test for session fixation vulnerabilities"""
        vulnerabilities = []

        login_endpoints = ['/login', '/signin', '/api/login', '/api/auth/login']

        for endpoint in login_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                # Get initial session
                resp1 = self.session.get(test_url, timeout=self.timeout, verify=False)
                cookies_before = self.session.cookies.get_dict()

                if not cookies_before:
                    continue

                # Simulate login
                login_resp = self.session.post(
                    test_url,
                    json={'username': 'test', 'password': 'test'},
                    timeout=self.timeout,
                    verify=False
                )

                cookies_after = self.session.cookies.get_dict()

                # Check if session ID changed after login
                session_changed = False
                for cookie_name in ['sessionid', 'session', 'PHPSESSID', 'JSESSIONID']:
                    if cookie_name in cookies_before and cookie_name in cookies_after:
                        if cookies_before[cookie_name] == cookies_after[cookie_name]:
                            vulnerabilities.append(VulnerabilitySchema(
                                type="session_fixation",
                                severity=SeverityEnum.HIGH,
                                url=test_url,
                                description="Session ID not regenerated after login",
                                evidence=f"Session cookie '{cookie_name}' remains same after authentication",
                                remediation="Regenerate session ID after successful authentication",
                                cwe="CWE-384",
                                cvss_score=7.5
                            ))
                            session_changed = True
                            break

                if session_changed:
                    break

            except Exception:
                continue

        return vulnerabilities

    def _test_session_hijacking(self, url: str) -> List[VulnerabilitySchema]:
        """Test for session hijacking vulnerabilities"""
        vulnerabilities = []

        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)
            cookies = self.session.cookies

            for cookie in cookies:
                # Check for secure flag
                if not cookie.secure and 'https' in url:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="missing_secure_flag",
                        severity=SeverityEnum.MEDIUM,
                        url=url,
                        description=f"Session cookie '{cookie.name}' lacks Secure flag",
                        evidence="Cookie can be transmitted over unencrypted connections",
                        remediation="Set Secure flag on all session cookies",
                        cwe="CWE-614",
                        cvss_score=5.3
                    ))

                # Check for HttpOnly flag
                if not cookie.has_nonstandard_attr('HttpOnly'):
                    vulnerabilities.append(VulnerabilitySchema(
                        type="missing_httponly_flag",
                        severity=SeverityEnum.MEDIUM,
                        url=url,
                        description=f"Session cookie '{cookie.name}' lacks HttpOnly flag",
                        evidence="Cookie accessible via JavaScript (XSS risk)",
                        remediation="Set HttpOnly flag on all session cookies",
                        cwe="CWE-1004",
                        cvss_score=5.3
                    ))

                # Check for SameSite attribute
                if not cookie.get_nonstandard_attr('SameSite'):
                    vulnerabilities.append(VulnerabilitySchema(
                        type="missing_samesite_attribute",
                        severity=SeverityEnum.MEDIUM,
                        url=url,
                        description=f"Session cookie '{cookie.name}' lacks SameSite attribute",
                        evidence="Cookie vulnerable to CSRF attacks",
                        remediation="Set SameSite=Strict or SameSite=Lax attribute",
                        cwe="CWE-352",
                        cvss_score=5.3
                    ))

        except Exception:
            pass

        return vulnerabilities

    def _test_mfa_bypass(self, url: str) -> List[VulnerabilitySchema]:
        """Test for MFA bypass vulnerabilities"""
        vulnerabilities = []

        mfa_endpoints = [
            '/mfa/verify',
            '/2fa/verify',
            '/api/mfa',
            '/verify-otp',
            '/two-factor'
        ]

        bypass_attempts = [
            {'code': '000000'},
            {'code': '123456'},
            {'code': ''},
            {'bypass': 'true'},
            {'skip_mfa': 'true'},
        ]

        for endpoint in mfa_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in bypass_attempts:
                try:
                    resp = self.session.post(
                        test_url,
                        json=payload,
                        timeout=self.timeout,
                        verify=False
                    )

                    if resp.status_code in [200, 302]:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="mfa_bypass",
                            severity=SeverityEnum.CRITICAL,
                            url=test_url,
                            description=f"MFA bypass possible with payload: {payload}",
                            evidence="MFA verification bypassed or weak validation",
                            remediation="Implement strict MFA validation, no bypass mechanisms",
                            cwe="CWE-287",
                            cvss_score=9.1
                        ))
                        break

                except Exception:
                    continue

            if vulnerabilities:
                break

        return vulnerabilities

    def _test_password_reset(self, url: str) -> List[VulnerabilitySchema]:
        """Test for password reset vulnerabilities"""
        vulnerabilities = []

        reset_endpoints = [
            '/forgot-password',
            '/reset-password',
            '/api/password-reset',
            '/api/forgot-password'
        ]

        for endpoint in reset_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                # Test account enumeration via password reset
                valid_email = 'admin@example.com'
                invalid_email = 'nonexistent_12345@example.com'

                resp1 = self.session.post(
                    test_url,
                    json={'email': valid_email},
                    timeout=self.timeout,
                    verify=False
                )

                resp2 = self.session.post(
                    test_url,
                    json={'email': invalid_email},
                    timeout=self.timeout,
                    verify=False
                )

                # Different responses = account enumeration
                if resp1.status_code != resp2.status_code or resp1.text != resp2.text:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="account_enumeration_reset",
                        severity=SeverityEnum.MEDIUM,
                        url=test_url,
                        description="Account enumeration via password reset",
                        evidence="Different responses for valid/invalid emails",
                        remediation="Return same response regardless of account existence",
                        cwe="CWE-203",
                        cvss_score=5.3
                    ))

                # Test predictable reset tokens
                reset_token_patterns = [
                    r'\d{6}',  # 6-digit numeric
                    r'\d{4}',  # 4-digit numeric
                    r'[a-f0-9]{32}',  # MD5 hash
                ]

                if resp1.status_code == 200:
                    for pattern in reset_token_patterns:
                        if re.search(pattern, resp1.text):
                            vulnerabilities.append(VulnerabilitySchema(
                                type="predictable_reset_token",
                                severity=SeverityEnum.HIGH,
                                url=test_url,
                                description="Password reset token appears predictable",
                                evidence=f"Token matches pattern: {pattern}",
                                remediation="Use cryptographically random tokens (min 128 bits)",
                                cwe="CWE-640",
                                cvss_score=7.5
                            ))
                            break

            except Exception:
                continue

        return vulnerabilities

    def _test_account_enumeration(self, url: str) -> List[VulnerabilitySchema]:
        """Test for account enumeration vulnerabilities"""
        vulnerabilities = []

        login_endpoints = ['/login', '/api/login', '/signin', '/api/auth/login']

        for endpoint in login_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                # Try with likely existing user
                resp1 = self.session.post(
                    test_url,
                    json={'username': 'admin', 'password': 'wrongpass'},
                    timeout=self.timeout,
                    verify=False
                )

                # Try with non-existing user
                resp2 = self.session.post(
                    test_url,
                    json={'username': 'nonexistent_user_99999', 'password': 'wrongpass'},
                    timeout=self.timeout,
                    verify=False
                )

                # Check for differences
                if resp1.status_code != resp2.status_code:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="account_enumeration_login",
                        severity=SeverityEnum.MEDIUM,
                        url=test_url,
                        description="Account enumeration via login response codes",
                        evidence=f"Status codes differ: {resp1.status_code} vs {resp2.status_code}",
                        remediation="Return same status code for valid/invalid users",
                        cwe="CWE-203",
                        cvss_score=5.3
                    ))

                elif resp1.text != resp2.text:
                    # Check for different error messages
                    if 'user' in resp1.text.lower() or 'password' in resp1.text.lower():
                        vulnerabilities.append(VulnerabilitySchema(
                            type="account_enumeration_message",
                            severity=SeverityEnum.MEDIUM,
                            url=test_url,
                            description="Account enumeration via different error messages",
                            evidence="Error messages reveal if username exists",
                            remediation="Use generic error message: 'Invalid credentials'",
                            cwe="CWE-203",
                            cvss_score=5.3
                        ))

            except Exception:
                continue

        return vulnerabilities

    def _test_session_timeout(self, url: str) -> List[VulnerabilitySchema]:
        """Test for session timeout configuration"""
        vulnerabilities = []

        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)
            cookies = self.session.cookies

            for cookie in cookies:
                # Check if session cookie has expiry
                if cookie.expires:
                    # Check if expiry is too long (> 1 day = 86400 seconds)
                    expiry_duration = cookie.expires - time.time()

                    if expiry_duration > 86400:  # > 24 hours
                        vulnerabilities.append(VulnerabilitySchema(
                            type="long_session_timeout",
                            severity=SeverityEnum.MEDIUM,
                            url=url,
                            description=f"Session cookie '{cookie.name}' has very long expiry",
                            evidence=f"Cookie expires in {int(expiry_duration/3600)} hours",
                            remediation="Set reasonable session timeout (15-30 minutes for sensitive apps)",
                            cwe="CWE-613",
                            cvss_score=5.3
                        ))
                else:
                    # Session cookie without expiry
                    vulnerabilities.append(VulnerabilitySchema(
                        type="no_session_expiry",
                        severity=SeverityEnum.LOW,
                        url=url,
                        description=f"Session cookie '{cookie.name}' has no expiry",
                        evidence="Cookie persists until browser closes",
                        remediation="Set explicit session timeout",
                        cwe="CWE-613",
                        cvss_score=3.7
                    ))

        except Exception:
            pass

        return vulnerabilities

    def _test_brute_force_protection(self, url: str) -> List[VulnerabilitySchema]:
        """Test for brute-force attack protection"""
        vulnerabilities = []

        login_endpoints = ['/login', '/api/login', '/signin']

        for endpoint in login_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                # Attempt multiple failed logins
                responses = []
                for i in range(10):
                    resp = self.session.post(
                        test_url,
                        json={'username': 'admin', 'password': f'wrongpass{i}'},
                        timeout=self.timeout,
                        verify=False
                    )
                    responses.append(resp.status_code)
                    time.sleep(0.1)

                # If no account lockout or CAPTCHA
                if all(status == responses[0] for status in responses):
                    vulnerabilities.append(VulnerabilitySchema(
                        type="no_brute_force_protection",
                        severity=SeverityEnum.HIGH,
                        url=test_url,
                        description="No brute-force protection detected",
                        evidence="10 failed login attempts without lockout or CAPTCHA",
                        remediation="Implement account lockout, CAPTCHA, or rate limiting after 3-5 failed attempts",
                        cwe="CWE-307",
                        cvss_score=7.5
                    ))

            except Exception:
                continue

        return vulnerabilities

    def _test_credential_stuffing(self, url: str) -> List[VulnerabilitySchema]:
        """Test for credential stuffing protection"""
        vulnerabilities = []

        login_endpoints = ['/login', '/api/login']

        # Common leaked credentials (for testing only)
        common_creds = [
            ('admin', 'admin'),
            ('admin', 'password'),
            ('test', 'test'),
            ('user', 'user'),
            ('root', 'root'),
        ]

        for endpoint in login_endpoints:
            test_url = urljoin(url, endpoint)

            successful_attempts = 0

            for username, password in common_creds:
                try:
                    resp = self.session.post(
                        test_url,
                        json={'username': username, 'password': password},
                        timeout=self.timeout,
                        verify=False
                    )

                    if resp.status_code in [200, 302]:
                        successful_attempts += 1

                except Exception:
                    continue

            if successful_attempts > 0:
                vulnerabilities.append(VulnerabilitySchema(
                    type="default_credentials",
                    severity=SeverityEnum.CRITICAL,
                    url=test_url,
                    description=f"Default credentials accepted ({successful_attempts} found)",
                    evidence="Common username/password combinations work",
                    remediation="Force password change on first login, disable default accounts",
                    cwe="CWE-798",
                    cvss_score=9.8
                ))

        return vulnerabilities
