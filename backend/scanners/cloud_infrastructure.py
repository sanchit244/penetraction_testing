"""
Cloud & Infrastructure Security Scanner - AWS/Azure/GCP metadata, cloud storage, containers
"""
import re
import json
from typing import List, Dict
from urllib.parse import urljoin
import requests
from models.schemas import VulnerabilitySchema, SeverityEnum


class CloudInfrastructureScanner:
    """Cloud and infrastructure security testing"""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def scan(self, url: str, depth: int = 2) -> List[VulnerabilitySchema]:
        """Run all cloud infrastructure checks"""
        vulnerabilities = []

        vulnerabilities.extend(self._test_cloud_metadata_exposure(url))
        vulnerabilities.extend(self._test_cloud_storage_buckets(url))
        vulnerabilities.extend(self._test_container_escape(url))
        vulnerabilities.extend(self._test_kubernetes_exposure(url))
        vulnerabilities.extend(self._test_docker_api_exposure(url))

        return vulnerabilities

    def _test_cloud_metadata_exposure(self, url: str) -> List[VulnerabilitySchema]:
        """Test for cloud metadata service exposure (AWS, Azure, GCP)"""
        vulnerabilities = []

        # Cloud metadata endpoints
        metadata_endpoints = [
            # AWS IMDSv1
            'http://169.254.169.254/latest/meta-data/',
            'http://169.254.169.254/latest/user-data/',
            'http://169.254.169.254/latest/dynamic/instance-identity/',

            # AWS IMDSv2 (requires token)
            'http://169.254.169.254/latest/api/token',

            # Azure
            'http://169.254.169.254/metadata/instance?api-version=2021-02-01',
            'http://169.254.169.254/metadata/identity/oauth2/token',

            # GCP
            'http://metadata.google.internal/computeMetadata/v1/',
            'http://169.254.169.254/computeMetadata/v1/',
        ]

        # Test SSRF to metadata service
        ssrf_endpoints = ['/api/fetch', '/api/proxy', '/api/webhook', '/download', '/fetch']

        for endpoint in ssrf_endpoints:
            test_url = urljoin(url, endpoint)

            for metadata_url in metadata_endpoints:
                try:
                    # Try to fetch metadata via SSRF
                    resp = self.session.post(
                        test_url,
                        json={'url': metadata_url},
                        timeout=self.timeout,
                        verify=False
                    )

                    # Check for metadata in response
                    if any(indicator in resp.text.lower() for indicator in
                           ['ami-id', 'instance-id', 'iam', 'credentials', 'metadata', 'access_token']):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="cloud_metadata_exposure",
                            severity=SeverityEnum.CRITICAL,
                            url=test_url,
                            description="Cloud metadata service accessible via SSRF",
                            evidence=f"Metadata endpoint accessible: {metadata_url}",
                            remediation="Implement SSRF protection, use IMDSv2 (AWS), block metadata IPs",
                            cwe="CWE-918",
                            cvss_score=9.8
                        ))
                        return vulnerabilities

                except Exception:
                    continue

        return vulnerabilities

    def _test_cloud_storage_buckets(self, url: str) -> List[VulnerabilitySchema]:
        """Test for exposed cloud storage buckets"""
        vulnerabilities = []

        try:
            # Get page content to find bucket references
            resp = self.session.get(url, timeout=self.timeout, verify=False)

            # S3 bucket patterns
            s3_patterns = [
                r'https?://([a-z0-9.-]+)\.s3\.amazonaws\.com',
                r'https?://s3\.amazonaws\.com/([a-z0-9.-]+)',
                r's3://([a-z0-9.-]+)',
            ]

            # Azure blob patterns
            azure_patterns = [
                r'https?://([a-z0-9]+)\.blob\.core\.windows\.net',
            ]

            # GCP storage patterns
            gcp_patterns = [
                r'https?://storage\.googleapis\.com/([a-z0-9.-]+)',
                r'gs://([a-z0-9.-]+)',
            ]

            all_patterns = s3_patterns + azure_patterns + gcp_patterns

            for pattern in all_patterns:
                matches = re.findall(pattern, resp.text)
                for bucket_name in matches:
                    # Test bucket accessibility
                    if 's3' in pattern:
                        test_urls = [
                            f'https://{bucket_name}.s3.amazonaws.com',
                            f'https://s3.amazonaws.com/{bucket_name}'
                        ]
                    elif 'blob' in pattern:
                        test_urls = [f'https://{bucket_name}.blob.core.windows.net']
                    else:
                        test_urls = [f'https://storage.googleapis.com/{bucket_name}']

                    for test_url in test_urls:
                        try:
                            bucket_resp = self.session.get(test_url, timeout=self.timeout, verify=False)

                            if bucket_resp.status_code == 200:
                                vulnerabilities.append(VulnerabilitySchema(
                                    type="public_cloud_storage",
                                    severity=SeverityEnum.HIGH,
                                    url=url,
                                    description=f"Publicly accessible cloud storage bucket: {bucket_name}",
                                    evidence=f"Bucket URL accessible: {test_url}",
                                    remediation="Configure proper access controls, enable bucket policies",
                                    cwe="CWE-284",
                                    cvss_score=7.5
                                ))

                        except Exception:
                            continue

        except Exception:
            pass

        return vulnerabilities

    def _test_container_escape(self, url: str) -> List[VulnerabilitySchema]:
        """Test for container escape vulnerabilities"""
        vulnerabilities = []

        # Container indicators in responses
        container_indicators = [
            '/.dockerenv',
            '/proc/self/cgroup',
            '/var/run/docker.sock',
            '/run/containerd',
        ]

        # Test path traversal to container files
        for indicator in container_indicators:
            test_url = urljoin(url, f'/api/download?file={indicator}')

            try:
                resp = self.session.get(test_url, timeout=self.timeout, verify=False)

                if resp.status_code == 200:
                    if 'docker' in resp.text.lower() or 'containerd' in resp.text.lower():
                        vulnerabilities.append(VulnerabilitySchema(
                            type="container_information_leak",
                            severity=SeverityEnum.MEDIUM,
                            url=test_url,
                            description=f"Container environment file accessible: {indicator}",
                            evidence="Container internals exposed via path traversal",
                            remediation="Restrict file access, implement proper path validation",
                            cwe="CWE-22",
                            cvss_score=5.3
                        ))

            except Exception:
                continue

        # Check for Docker socket exposure
        docker_endpoints = ['/var/run/docker.sock', '/run/docker.sock']
        for endpoint in docker_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                resp = self.session.get(test_url, timeout=self.timeout, verify=False)

                if resp.status_code == 200:
                    vulnerabilities.append(VulnerabilitySchema(
                        type="docker_socket_exposure",
                        severity=SeverityEnum.CRITICAL,
                        url=test_url,
                        description="Docker socket exposed - container escape possible",
                        evidence="Docker socket accessible via HTTP",
                        remediation="Never expose Docker socket, use proper container isolation",
                        cwe="CWE-284",
                        cvss_score=9.8
                    ))

            except Exception:
                continue

        return vulnerabilities

    def _test_kubernetes_exposure(self, url: str) -> List[VulnerabilitySchema]:
        """Test for Kubernetes exposure"""
        vulnerabilities = []

        # Kubernetes API endpoints
        k8s_endpoints = [
            '/api/v1',
            '/apis',
            '/api/v1/namespaces',
            '/api/v1/pods',
            '/api/v1/secrets',
            '/healthz',
            '/version',
        ]

        for endpoint in k8s_endpoints:
            test_url = urljoin(url, endpoint)

            try:
                resp = self.session.get(test_url, timeout=self.timeout, verify=False)

                if resp.status_code == 200:
                    # Check for Kubernetes API responses
                    if any(keyword in resp.text.lower() for keyword in ['kubernetes', 'k8s', 'apiversion', 'kind']):
                        vulnerabilities.append(VulnerabilitySchema(
                            type="kubernetes_api_exposure",
                            severity=SeverityEnum.CRITICAL,
                            url=test_url,
                            description=f"Kubernetes API endpoint exposed: {endpoint}",
                            evidence="Kubernetes API accessible without authentication",
                            remediation="Enable RBAC, require authentication, restrict access",
                            cwe="CWE-306",
                            cvss_score=9.8
                        ))

            except Exception:
                continue

        # Check for service account token
        token_path = '/var/run/secrets/kubernetes.io/serviceaccount/token'
        test_url = urljoin(url, f'/api/file?path={token_path}')

        try:
            resp = self.session.get(test_url, timeout=self.timeout, verify=False)

            if resp.status_code == 200 and len(resp.text) > 50:
                vulnerabilities.append(VulnerabilitySchema(
                    type="k8s_service_account_token_leak",
                    severity=SeverityEnum.CRITICAL,
                    url=test_url,
                    description="Kubernetes service account token exposed",
                    evidence="Service account token accessible via application",
                    remediation="Restrict file access, use proper RBAC, mount tokens read-only",
                    cwe="CWE-200",
                    cvss_score=9.1
                ))

        except Exception:
            pass

        return vulnerabilities

    def _test_docker_api_exposure(self, url: str) -> List[VulnerabilitySchema]:
        """Test for Docker API exposure"""
        vulnerabilities = []

        # Docker API ports
        docker_ports = [2375, 2376]

        parsed = requests.utils.urlparse(url)
        base_host = parsed.netloc.split(':')[0]

        for port in docker_ports:
            test_url = f'http://{base_host}:{port}/version'

            try:
                resp = self.session.get(test_url, timeout=5, verify=False)

                if resp.status_code == 200:
                    if 'docker' in resp.text.lower() or 'apiversion' in resp.text.lower():
                        vulnerabilities.append(VulnerabilitySchema(
                            type="docker_api_exposed",
                            severity=SeverityEnum.CRITICAL,
                            url=test_url,
                            description=f"Docker API exposed on port {port}",
                            evidence="Docker API accessible without authentication",
                            remediation="Disable remote API or enable TLS authentication",
                            cwe="CWE-306",
                            cvss_score=9.8
                        ))

            except Exception:
                continue

        return vulnerabilities
