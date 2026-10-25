"""
API Security Scanner - Tests REST API, GraphQL, JWT, and authentication bypass vulnerabilities
"""
import re
import json
import base64
import jwt as pyjwt
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import requests
from models.schemas import VulnerabilitySchema, SeverityEnum


class APISecurityScanner:
    """Comprehensive API security testing"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VulnScanner-API/1.0'
        })

    def scan(self, url: str, depth: int = 2) -> List[VulnerabilitySchema]:
        """Run all API security checks"""
        vulnerabilities = []

        vulnerabilities.extend(self._test_api_endpoints(url, depth))
        vulnerabilities.extend(self._test_graphql_security(url))
        vulnerabilities.extend(self._test_jwt_vulnerabilities(url))
        vulnerabilities.extend(self._test_rate_limiting(url))
        vulnerabilities.extend(self._test_api_authentication_bypass(url))
        vulnerabilities.extend(self._test_bola_idor(url))
        vulnerabilities.extend(self._test_mass_assignment(url))

        return vulnerabilities

    def _test_api_endpoints(self, url: str, depth: int) -> List[VulnerabilitySchema]:
        """Discover and test REST API endpoints"""
        vulnerabilities = []

        # Common API paths
        api_paths = [
            '/api', '/api/v1', '/api/v2', '/rest', '/graphql',
            '/swagger.json', '/openapi.json', '/api-docs',
            '/api/users', '/api/admin', '/api/config'
        ]

        for path in api_paths:
            test_url = urljoin(url, path)
            try:
                resp = self.session.get(test_url, timeout=self.timeout, verify=False)

                # Check for exposed API documentation
                if resp.status_code == 200:
                    if any(keyword in resp.text.lower() for keyword in ['swagger', 'openapi', 'api documentation']):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="api_documentation_exposure",
                            severity=SeverityEnum.MEDIUM,
                            url=test_url,
                            description=f"API documentation exposed at {path}",
                            evidence=f"Status: {resp.status_code}",
                            remediation="Restrict access to API documentation in production",
                            cwe="CWE-200",
                            cvss_score=5.3
                        ))

                    # Check for unauthenticated API access
                    if self._is_sensitive_data(resp.text):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="unauthenticated_api_access",
                            severity=SeverityEnum.HIGH,
                            url=test_url,
                            description="Sensitive API endpoint accessible without authentication",
                            evidence=f"Endpoint returns sensitive data without auth",
                            remediation="Implement authentication and authorization for API endpoints",
                            cwe="CWE-306",
                            cvss_score=7.5
                        ))

                # Test for verbose error messages
                bad_request_url = f"{test_url}/nonexistent-endpoint-12345"
                resp = self.session.get(bad_request_url, timeout=self.timeout, verify=False)
                if resp.status_code in [400, 404, 500]:
                    if self._has_verbose_errors(resp.text):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="api_verbose_errors",
                            severity=SeverityEnum.LOW,
                            url=test_url,
                            description="API returns verbose error messages with sensitive information",
                            evidence=f"Error response contains stack traces or internal paths",
                            remediation="Implement generic error messages for production",
                            cwe="CWE-209",
                            cvss_score=3.7
                        ))

            except Exception as e:
                continue

        return vulnerabilities

    def _test_graphql_security(self, url: str) -> List[VulnerabilitySchema]:
        """Test GraphQL-specific vulnerabilities"""
        vulnerabilities = []

        graphql_endpoints = ['/graphql', '/api/graphql', '/v1/graphql', '/query']

        for endpoint in graphql_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                # Test introspection enabled
                introspection_query = {
                    "query": """
                    {
                        __schema {
                            types {
                                name
                            }
                        }
                    }
                    """
                }

                resp = self.session.post(
                    test_url,
                    json=introspection_query,
                    timeout=self.timeout,
                    verify=False
                )

                if resp.status_code == 200 and '__schema' in resp.text:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="graphql_introspection_enabled",
                        severity=SeverityEnum.MEDIUM,
                        url=test_url,
                        description="GraphQL introspection is enabled in production",
                        evidence="Introspection query returned schema information",
                        remediation="Disable GraphQL introspection in production environments",
                        cwe="CWE-200",
                        cvss_score=5.3
                    ))

                # Test query depth (DoS via nested queries)
                deep_query = self._generate_deep_graphql_query(depth=15)
                resp = self.session.post(
                    test_url,
                    json={"query": deep_query},
                    timeout=self.timeout,
                    verify=False
                )

                if resp.status_code == 200:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="graphql_no_depth_limit",
                        severity=SeverityEnum.MEDIUM,
                        url=test_url,
                        description="GraphQL endpoint lacks query depth limiting",
                        evidence="Deep nested query (15 levels) was accepted",
                        remediation="Implement query depth and complexity limits",
                        cwe="CWE-400",
                        cvss_score=5.3
                    ))

                # Test batching attacks
                batch_queries = [{"query": "{__typename}"} for _ in range(100)]
                resp = self.session.post(
                    test_url,
                    json=batch_queries,
                    timeout=self.timeout,
                    verify=False
                )

                if resp.status_code == 200:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="graphql_batch_attack",
                        severity=SeverityEnum.MEDIUM,
                        url=test_url,
                        description="GraphQL allows unrestricted batch queries",
                        evidence="100 batched queries accepted without restriction",
                        remediation="Implement batch query limits and rate limiting",
                        cwe="CWE-770",
                        cvss_score=5.3
                    ))

            except Exception:
                continue

        return vulnerabilities

    def _test_jwt_vulnerabilities(self, url: str) -> List[VulnerabilitySchema]:
        """Test JWT token security issues"""
        vulnerabilities = []

        # Try to find JWT tokens in responses
        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False)

            # Look for JWT patterns in response
            jwt_pattern = r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'
            tokens = re.findall(jwt_pattern, resp.text)

            for token in tokens:
                try:
                    # Decode without verification
                    header = pyjwt.get_unverified_header(token)
                    payload = pyjwt.decode(token, options={"verify_signature": False})

                    # Check for 'none' algorithm
                    if header.get('alg', '').lower() == 'none':
                        vulnerabilities.append(VulnerabilitySchema(
                            type="jwt_none_algorithm",
                            severity=SeverityEnum.CRITICAL,
                            url=url,
                            description="JWT token uses 'none' algorithm - can be forged",
                            evidence=f"Algorithm: {header.get('alg')}",
                            remediation="Use strong signing algorithms (RS256, HS256) and validate 'alg' header",
                            cwe="CWE-347",
                            cvss_score=9.8
                        ))

                    # Check for weak secret (try common secrets)
                    weak_secrets = ['secret', 'password', '123456', 'qwerty', 'your-secret-key']
                    for secret in weak_secrets:
                        try:
                            pyjwt.decode(token, secret, algorithms=["HS256"])
                            vulnerabilities.append(VulnerabilitySchema(
                                type="jwt_weak_secret",
                                severity=SeverityEnum.CRITICAL,
                                url=url,
                                description=f"JWT token signed with weak secret: '{secret}'",
                                evidence=f"Token successfully decoded with weak secret",
                                remediation="Use strong, randomly generated secrets (min 256 bits)",
                                cwe="CWE-326",
                                cvss_score=9.1
                            ))
                            break
                        except:
                            continue

                    # Check for missing expiration
                    if 'exp' not in payload:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="jwt_no_expiration",
                            severity=SeverityEnum.HIGH,
                            url=url,
                            description="JWT token lacks expiration claim",
                            evidence="No 'exp' field in token payload",
                            remediation="Always set expiration time for JWT tokens",
                            cwe="CWE-613",
                            cvss_score=7.5
                        ))

                    # Check for sensitive data in payload
                    sensitive_fields = ['password', 'secret', 'ssn', 'credit_card']
                    for field in sensitive_fields:
                        if field in str(payload).lower():
                            vulnerabilities.append(VulnerabilitySchema(
                                type="jwt_sensitive_data",
                                severity=SeverityEnum.HIGH,
                                url=url,
                                description=f"JWT token contains sensitive data: {field}",
                                evidence="Sensitive information stored in token payload",
                                remediation="Avoid storing sensitive data in JWT payloads",
                                cwe="CWE-312",
                                cvss_score=7.5
                            ))
                            break

                except Exception:
                    continue

        except Exception:
            pass

        return vulnerabilities

    def _test_rate_limiting(self, url: str) -> List[VulnerabilitySchema]:
        """Test for rate limiting and brute-force protection"""
        vulnerabilities = []

        try:
            # Send multiple rapid requests
            responses = []
            for _ in range(20):
                resp = self.session.get(url, timeout=self.timeout, verify=False)
                responses.append(resp.status_code)

            # Check if rate limiting is applied
            if all(status != 429 for status in responses):
                vulnerabilities.append(VulnerabilitySchema(
                    type="no_rate_limiting",
                    severity=SeverityEnum.MEDIUM,
                    url=url,
                    description="API endpoint lacks rate limiting protection",
                    evidence="20 rapid requests accepted without rate limiting",
                    remediation="Implement rate limiting (e.g., 100 requests/minute per IP)",
                    cwe="CWE-770",
                    cvss_score=5.3
                ))

        except Exception:
            pass

        return vulnerabilities

    def _test_api_authentication_bypass(self, url: str) -> List[VulnerabilitySchema]:
        """Test for authentication bypass vulnerabilities"""
        vulnerabilities = []

        # Test various bypass techniques
        bypass_headers = [
            {'X-Original-URL': '/admin'},
            {'X-Rewrite-URL': '/admin'},
            {'X-Forwarded-For': '127.0.0.1'},
            {'X-Custom-IP-Authorization': '127.0.0.1'},
            {'X-Originating-IP': '127.0.0.1'},
        ]

        api_endpoints = ['/api/admin', '/api/users', '/api/config']

        for endpoint in api_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                # Normal request (should fail)
                normal_resp = self.session.get(test_url, timeout=self.timeout, verify=False)

                # Try bypass headers
                for headers in bypass_headers:
                    bypass_resp = self.session.get(
                        test_url,
                        headers=headers,
                        timeout=self.timeout,
                        verify=False
                    )

                    if bypass_resp.status_code == 200 and normal_resp.status_code in [401, 403]:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="authentication_bypass",
                            severity=SeverityEnum.CRITICAL,
                            url=test_url,
                            description=f"Authentication bypass via header: {list(headers.keys())[0]}",
                            evidence=f"Normal: {normal_resp.status_code}, Bypass: {bypass_resp.status_code}",
                            remediation="Properly validate authentication on server-side, ignore client headers",
                            cwe="CWE-288",
                            cvss_score=9.8
                        ))
                        break

            except Exception:
                continue

        return vulnerabilities

    def _test_bola_idor(self, url: str) -> List[VulnerabilitySchema]:
        """Test for Broken Object Level Authorization (BOLA/IDOR)"""
        vulnerabilities = []

        # Common IDOR patterns
        idor_patterns = [
            '/api/users/{id}',
            '/api/profile/{id}',
            '/api/documents/{id}',
            '/api/orders/{id}'
        ]

        for pattern in idor_patterns:
            # Test with different IDs
            test_ids = ['1', '2', '999', 'admin', '../../etc/passwd']

            for test_id in test_ids:
                endpoint = pattern.replace('{id}', test_id)
                test_url = urljoin(url, endpoint)

                try:
                    resp = self.session.get(test_url, timeout=self.timeout, verify=False)

                    if resp.status_code == 200 and self._is_sensitive_data(resp.text):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="idor_vulnerability",
                            severity=SeverityEnum.HIGH,
                            url=test_url,
                            description=f"IDOR vulnerability - unauthorized access to {endpoint}",
                            evidence=f"ID {test_id} accessible without proper authorization",
                            remediation="Implement proper authorization checks for object access",
                            cwe="CWE-639",
                            cvss_score=7.5
                        ))
                        break

                except Exception:
                    continue

        return vulnerabilities

    def _test_mass_assignment(self, url: str) -> List[VulnerabilitySchema]:
        """Test for mass assignment vulnerabilities"""
        vulnerabilities = []

        # Test POST/PUT endpoints with extra parameters
        test_endpoints = ['/api/users', '/api/profile', '/api/settings']

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            # Try adding admin/role parameters
            payloads = [
                {'name': 'test', 'role': 'admin', 'isAdmin': True},
                {'name': 'test', 'is_admin': True, 'privileges': 'all'},
                {'name': 'test', 'user_type': 'admin', 'permissions': ['admin']},
            ]

            for payload in payloads:
                try:
                    resp = self.session.post(
                        test_url,
                        json=payload,
                        timeout=self.timeout,
                        verify=False
                    )

                    if resp.status_code in [200, 201]:
                        # Check if extra fields were accepted
                        if any(field in resp.text.lower() for field in ['admin', 'role', 'privilege']):
                            vulnerabilities.append(VulnerabilitySchema(
                                type="mass_assignment",
                                severity=SeverityEnum.HIGH,
                                url=test_url,
                                description="Mass assignment vulnerability - can modify privileged fields",
                                evidence=f"Extra fields accepted: {list(payload.keys())}",
                                remediation="Use allow-lists for accepted parameters, ignore unexpected fields",
                                cwe="CWE-915",
                                cvss_score=7.5
                            ))
                            break

                except Exception:
                    continue

        return vulnerabilities

    def _generate_deep_graphql_query(self, depth: int) -> str:
        """Generate deeply nested GraphQL query for DoS testing"""
        query = "{ user { "
        for i in range(depth):
            query += "profile { "
        query += "id "
        query += "} " * (depth + 1)
        return query

    def _is_sensitive_data(self, text: str) -> bool:
        """Check if response contains sensitive data"""
        sensitive_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{16}\b',  # Credit card
            r'"password"\s*:\s*"[^"]+"',  # Password in JSON
            r'api[_-]?key',  # API keys
            r'secret',  # Secrets
        ]

        return any(re.search(pattern, text, re.IGNORECASE) for pattern in sensitive_patterns)

    def _has_verbose_errors(self, text: str) -> bool:
        """Check for verbose error messages"""
        error_indicators = [
            'traceback', 'stack trace', 'exception',
            'at line', 'File "/', 'in <module>',
            'SQLException', 'NullPointerException',
            'root@', '/home/', '/var/www/'
        ]

        return any(indicator in text for indicator in error_indicators)
