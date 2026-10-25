"""
Business Logic Vulnerability Scanner - Tests race conditions, parameter tampering, workflow bypass
"""
import time
import threading
from typing import List, Dict
from urllib.parse import urljoin, parse_qs, urlparse
import requests
from concurrent.futures import ThreadPoolExecutor
from models.schemas import VulnerabilitySchema, SeverityEnum


class BusinessLogicScanner:
    """Business logic and workflow vulnerability testing"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def scan(self, url: str, depth: int = 2) -> List[VulnerabilitySchema]:
        """Run all business logic checks"""
        vulnerabilities = []

        vulnerabilities.extend(self._test_race_conditions(url))
        vulnerabilities.extend(self._test_parameter_tampering(url))
        vulnerabilities.extend(self._test_workflow_bypass(url))
        vulnerabilities.extend(self._test_negative_values(url))
        vulnerabilities.extend(self._test_quantity_manipulation(url))
        vulnerabilities.extend(self._test_price_manipulation(url))
        vulnerabilities.extend(self._test_coupon_reuse(url))
        vulnerabilities.extend(self._test_session_puzzling(url))

        return vulnerabilities

    def _test_race_conditions(self, url: str) -> List[VulnerabilitySchema]:
        """Test for race condition vulnerabilities"""
        vulnerabilities = []

        # Test endpoints susceptible to race conditions
        test_endpoints = [
            '/api/cart/checkout',
            '/api/wallet/transfer',
            '/api/redemption',
            '/api/vote',
            '/api/purchase'
        ]

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                # Simulate concurrent requests
                results = []

                def make_request():
                    try:
                        resp = self.session.post(
                            test_url,
                            json={'amount': 10, 'item_id': 1},
                            timeout=self.timeout,
                            verify=False
                        )
                        return resp.status_code
                    except:
                        return None

                # Launch 10 simultaneous requests
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(make_request) for _ in range(10)]
                    results = [f.result() for f in futures]

                # Check if multiple succeeded (race condition indicator)
                success_count = sum(1 for r in results if r in [200, 201])

                if success_count > 1:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="race_condition",
                        severity=SeverityEnum.HIGH,
                        url=test_url,
                        description=f"Race condition vulnerability - {success_count}/10 concurrent requests succeeded",
                        evidence=f"Multiple concurrent operations completed without proper locking",
                        remediation="Implement database-level locks, transaction isolation, or idempotency keys",
                        cwe="CWE-362",
                        cvss_score=7.4
                    ))

            except Exception:
                continue

        return vulnerabilities

    def _test_parameter_tampering(self, url: str) -> List[VulnerabilitySchema]:
        """Test for parameter tampering vulnerabilities"""
        vulnerabilities = []

        # Test price/quantity parameter tampering
        tampering_tests = [
            {
                'endpoint': '/api/cart/add',
                'params': [
                    {'item_id': 1, 'price': 0.01},
                    {'item_id': 1, 'price': -10},
                    {'item_id': 1, 'quantity': 999999},
                    {'item_id': 1, 'discount': 100},
                ]
            },
            {
                'endpoint': '/api/purchase',
                'params': [
                    {'user_id': 1, 'role': 'admin'},
                    {'order_id': 1, 'status': 'completed'},
                    {'product_id': 1, 'is_free': True},
                ]
            }
        ]

        for test in tampering_tests:
            test_url = urljoin(url, test['endpoint'])

            for params in test['params']:
                try:
                    resp = self.session.post(
                        test_url,
                        json=params,
                        timeout=self.timeout,
                        verify=False
                    )

                    # If tampered params accepted (200/201)
                    if resp.status_code in [200, 201]:
                        tampered_field = next(
                            (k for k in params.keys()
                             if k in ['price', 'role', 'status', 'is_free', 'discount']),
                            'unknown'
                        )

                        vulnerabilities.append(VulnerabilitySchema(
                            type="parameter_tampering",
                            severity=SeverityEnum.HIGH,
                            url=test_url,
                            description=f"Parameter tampering vulnerability - can modify {tampered_field}",
                            evidence=f"Tampered parameter accepted: {tampered_field}={params[tampered_field]}",
                            remediation="Validate all parameters server-side, use server-calculated values for sensitive fields",
                            cwe="CWE-472",
                            cvss_score=7.5
                        ))
                        break

                except Exception:
                    continue

        return vulnerabilities

    def _test_workflow_bypass(self, url: str) -> List[VulnerabilitySchema]:
        """Test for workflow step bypass vulnerabilities"""
        vulnerabilities = []

        # Common multi-step workflows
        workflows = [
            {
                'name': 'checkout',
                'steps': ['/cart', '/checkout', '/payment', '/confirm'],
                'bypass_to': '/confirm'
            },
            {
                'name': 'registration',
                'steps': ['/register', '/verify-email', '/complete'],
                'bypass_to': '/complete'
            },
            {
                'name': 'password_reset',
                'steps': ['/forgot-password', '/verify-token', '/reset-password'],
                'bypass_to': '/reset-password'
            }
        ]

        for workflow in workflows:
            bypass_url = urljoin(url, workflow['bypass_to'])

            try:
                # Try to access final step directly
                resp = self.session.get(bypass_url, timeout=self.timeout, verify=False)

                # Also try POST
                post_resp = self.session.post(
                    bypass_url,
                    json={'user_id': 1, 'action': 'complete'},
                    timeout=self.timeout,
                    verify=False
                )

                if resp.status_code == 200 or post_resp.status_code in [200, 201]:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="workflow_bypass",
                        severity=SeverityEnum.HIGH,
                        url=bypass_url,
                        description=f"Workflow bypass - can skip steps in {workflow['name']} process",
                        evidence=f"Direct access to final step without completing prerequisites",
                        remediation="Implement server-side state validation for multi-step processes",
                        cwe="CWE-840",
                        cvss_score=7.5
                    ))

            except Exception:
                continue

        return vulnerabilities

    def _test_negative_values(self, url: str) -> List[VulnerabilitySchema]:
        """Test for negative value handling issues"""
        vulnerabilities = []

        test_endpoints = [
            '/api/cart/add',
            '/api/wallet/deposit',
            '/api/points/add',
            '/api/transfer'
        ]

        negative_payloads = [
            {'amount': -100, 'item_id': 1},
            {'quantity': -10, 'product_id': 1},
            {'price': -50, 'order_id': 1},
            {'points': -1000, 'user_id': 1}
        ]

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in negative_payloads:
                try:
                    resp = self.session.post(
                        test_url,
                        json=payload,
                        timeout=self.timeout,
                        verify=False
                    )

                    if resp.status_code in [200, 201]:
                        negative_field = next(
                            (k for k, v in payload.items() if isinstance(v, int) and v < 0),
                            'amount'
                        )

                        vulnerabilities.append(VulnerabilitySchema(
                            type="negative_value_bypass",
                            severity=SeverityEnum.HIGH,
                            url=test_url,
                            description=f"Accepts negative values for {negative_field}",
                            evidence=f"Negative value accepted: {negative_field}={payload[negative_field]}",
                            remediation="Validate that monetary/quantity fields are non-negative",
                            cwe="CWE-20",
                            cvss_score=7.5
                        ))
                        break

                except Exception:
                    continue

        return vulnerabilities

    def _test_quantity_manipulation(self, url: str) -> List[VulnerabilitySchema]:
        """Test for quantity manipulation vulnerabilities"""
        vulnerabilities = []

        test_endpoints = ['/api/cart/add', '/api/order/create', '/api/purchase']

        extreme_quantities = [
            {'quantity': 999999999, 'item_id': 1},
            {'quantity': 2147483647, 'item_id': 1},  # Max int
            {'quantity': 0, 'item_id': 1},  # Zero quantity
        ]

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in extreme_quantities:
                try:
                    resp = self.session.post(
                        test_url,
                        json=payload,
                        timeout=self.timeout,
                        verify=False
                    )

                    if resp.status_code in [200, 201]:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="quantity_manipulation",
                            severity=SeverityEnum.MEDIUM,
                            url=test_url,
                            description=f"Extreme quantity accepted: {payload['quantity']}",
                            evidence="No proper quantity validation",
                            remediation="Implement realistic quantity limits and validation",
                            cwe="CWE-20",
                            cvss_score=5.3
                        ))
                        break

                except Exception:
                    continue

        return vulnerabilities

    def _test_price_manipulation(self, url: str) -> List[VulnerabilitySchema]:
        """Test for client-side price manipulation"""
        vulnerabilities = []

        test_endpoints = ['/api/checkout', '/api/order', '/api/payment']

        price_payloads = [
            {'total': 0.01, 'items': [{'id': 1, 'price': 0.01}]},
            {'total': 1, 'items': [{'id': 1, 'price': 1}]},  # Way below real price
            {'amount': 0, 'product_id': 1},
        ]

        for endpoint in test_endpoints:
            test_url = urljoin(url, endpoint)

            for payload in price_payloads:
                try:
                    resp = self.session.post(
                        test_url,
                        json=payload,
                        timeout=self.timeout,
                        verify=False
                    )

                    if resp.status_code in [200, 201, 202]:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="price_manipulation",
                            severity=SeverityEnum.CRITICAL,
                            url=test_url,
                            description="Client-controlled price accepted by server",
                            evidence=f"Manipulated price payload accepted: {payload}",
                            remediation="Calculate prices server-side, never trust client-provided amounts",
                            cwe="CWE-642",
                            cvss_score=9.1
                        ))
                        break

                except Exception:
                    continue

        return vulnerabilities

    def _test_coupon_reuse(self, url: str) -> List[VulnerabilitySchema]:
        """Test for coupon/voucher reuse vulnerabilities"""
        vulnerabilities = []

        coupon_endpoints = ['/api/apply-coupon', '/api/redeem', '/api/voucher']

        test_coupon = 'TEST_COUPON_123'

        for endpoint in coupon_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                # Try to apply same coupon multiple times
                responses = []
                for _ in range(5):
                    resp = self.session.post(
                        test_url,
                        json={'coupon_code': test_coupon, 'order_id': 1},
                        timeout=self.timeout,
                        verify=False
                    )
                    responses.append(resp.status_code)
                    time.sleep(0.1)

                # If multiple successes, coupon can be reused
                success_count = sum(1 for r in responses if r in [200, 201])

                if success_count > 1:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="coupon_reuse",
                        severity=SeverityEnum.HIGH,
                        url=test_url,
                        description=f"Coupon can be reused multiple times ({success_count}/5)",
                        evidence="Same coupon code accepted multiple times",
                        remediation="Implement one-time use tracking for coupons/vouchers",
                        cwe="CWE-841",
                        cvss_score=7.5
                    ))

            except Exception:
                continue

        return vulnerabilities

    def _test_session_puzzling(self, url: str) -> List[VulnerabilitySchema]:
        """Test for session puzzling vulnerabilities"""
        vulnerabilities = []

        try:
            # Create two sessions
            session1 = requests.Session()
            session2 = requests.Session()

            # Login with different users (simulated)
            test_endpoints = ['/api/login', '/api/profile', '/api/account']

            for endpoint in test_endpoints:
                test_url = urljoin(url, endpoint)

                # Get session1 cookie
                resp1 = session1.get(test_url, timeout=self.timeout, verify=False)
                cookies1 = session1.cookies.get_dict()

                # Use session1 cookies in session2
                if cookies1:
                    resp2 = session2.get(
                        test_url,
                        cookies=cookies1,
                        timeout=self.timeout,
                        verify=False
                    )

                    if resp2.status_code == 200:
                        vulnerabilities.append(VulnerabilitySchema(
                            type="session_puzzling",
                            severity=SeverityEnum.MEDIUM,
                            url=test_url,
                            description="Session tokens may be susceptible to session puzzling",
                            evidence="Session cookie accepted across different contexts",
                            remediation="Bind sessions to specific user context and IP address",
                            cwe="CWE-384",
                            cvss_score=6.5
                        ))
                        break

        except Exception:
            pass

        return vulnerabilities
